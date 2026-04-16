"""Regras backend de FAQ, qualificacao e transferencia por departamento."""

from dataclasses import dataclass
import re
import unicodedata
from typing import Literal

IntentType = Literal["faq", "qualification", "transfer", "general"]

DEFAULT_DEPARTMENT_IDS: dict[str, str] = {
    "sales": "department_sales",
    "support": "department_support",
    "financial": "department_financial",
    "human_handoff": "department_human_handoff",
}

FAQ_RULES: tuple[tuple[str, tuple[str, ...], str], ...] = (
    (
        "business_hours",
        ("horario", "atendimento", "funcionamento"),
        "Nosso horario de atendimento e em horario comercial. Posso te encaminhar para um atendente humano para confirmar detalhes atualizados.",
    ),
    (
        "pricing",
        ("preco", "valor", "quanto custa", "orcamento"),
        "Temos opcoes conforme a necessidade. Se quiser, eu te faco algumas perguntas rapidas para te direcionar para a melhor proposta.",
    ),
    (
        "location",
        ("endereco", "localizacao", "onde fica"),
        "Atendemos de forma remota e/ou presencial conforme operacao do cliente. Se preferir, te encaminho para o time responsavel confirmar disponibilidade.",
    ),
)

GOAL_KEYWORDS = (
    "quero contratar",
    "quero comprar",
    "tenho interesse",
    "gostaria de contratar",
    "proposta",
    "plano",
    "servico",
)
_BUDGET_KEYWORDS = ("orcamento", "investir", "valor", "preco", "ate")
_TIMELINE_KEYWORDS = ("hoje", "urgente", "esta semana", "este mes", "prazo", "quando")

_HUMAN_HANDOFF_KEYWORDS = ("atendente", "humano", "pessoa", "falar com alguem")
_FINANCIAL_KEYWORDS = ("fatura", "boleto", "pagamento", "reembolso", "financeiro")
_SUPPORT_KEYWORDS = ("erro", "nao funciona", "problema", "reclamacao", "suporte")


@dataclass(frozen=True, slots=True)
class FaqResolution:
    """Representa FAQ reconhecida por regra de palavra-chave."""

    key: str
    answer: str


@dataclass(frozen=True, slots=True)
class QualificationResult:
    """Resumo da qualificacao do lead a partir da mensagem recebida."""

    has_goal: bool
    has_budget_signal: bool
    has_timeline_signal: bool
    is_ready_for_handoff: bool
    missing_fields: tuple[str, ...]
    next_question: str | None


@dataclass(frozen=True, slots=True)
class DepartmentTransferDecision:
    """Decisao de transferencia para departamento especifico."""

    should_transfer: bool
    department_key: str | None
    department_id: str | None
    reason: str | None


@dataclass(frozen=True, slots=True)
class ConversationRulesDecision:
    """Saida consolidada das regras de FAQ, qualificacao e transferencia."""

    intent: IntentType
    faq: FaqResolution | None
    qualification: QualificationResult
    transfer: DepartmentTransferDecision


def evaluate_conversation_rules(
    message: str,
    *,
    department_ids: dict[str, str] | None = None,
) -> ConversationRulesDecision:
    """Avalia mensagem recebida e retorna decisao de orquestracao conversacional."""
    normalized_message = _normalize_message(message)
    if not normalized_message:
        raise ValueError("message deve ser informado para avaliar regras de conversa.")

    qualification = _evaluate_qualification(normalized_message)
    faq = None if qualification.has_goal else _match_faq(normalized_message)
    transfer = _evaluate_department_transfer(
        normalized_message,
        qualification=qualification,
        department_catalog=_resolve_department_catalog(department_ids),
    )

    intent = _resolve_intent(faq=faq, qualification=qualification, transfer=transfer)
    return ConversationRulesDecision(intent=intent, faq=faq, qualification=qualification, transfer=transfer)


def _resolve_department_catalog(custom_department_ids: dict[str, str] | None) -> dict[str, str]:
    if not custom_department_ids:
        return dict(DEFAULT_DEPARTMENT_IDS)

    resolved = dict(DEFAULT_DEPARTMENT_IDS)
    resolved.update(custom_department_ids)
    return resolved


def _match_faq(normalized_message: str) -> FaqResolution | None:
    for key, keywords, answer in FAQ_RULES:
        if _contains_any_keyword(normalized_message, keywords):
            return FaqResolution(key=key, answer=answer)

    return None


def _evaluate_qualification(normalized_message: str) -> QualificationResult:
    has_goal = _contains_any_keyword(normalized_message, GOAL_KEYWORDS)
    has_budget_signal = _contains_any_keyword(normalized_message, _BUDGET_KEYWORDS)
    has_timeline_signal = _contains_any_keyword(normalized_message, _TIMELINE_KEYWORDS)

    missing_fields: list[str] = []
    if not has_goal:
        missing_fields.append("goal")
    if not has_budget_signal:
        missing_fields.append("budget")
    if not has_timeline_signal:
        missing_fields.append("timeline")

    is_ready_for_handoff = has_goal and has_budget_signal and has_timeline_signal

    next_question = _resolve_next_qualification_question(missing_fields)
    return QualificationResult(
        has_goal=has_goal,
        has_budget_signal=has_budget_signal,
        has_timeline_signal=has_timeline_signal,
        is_ready_for_handoff=is_ready_for_handoff,
        missing_fields=tuple(missing_fields),
        next_question=next_question,
    )


def _evaluate_department_transfer(
    normalized_message: str,
    *,
    qualification: QualificationResult,
    department_catalog: dict[str, str],
) -> DepartmentTransferDecision:
    if _contains_any_keyword(normalized_message, _HUMAN_HANDOFF_KEYWORDS):
        return _build_transfer_decision(
            department_key="human_handoff",
            department_catalog=department_catalog,
            reason="Cliente pediu atendimento humano explicitamente.",
        )

    if _contains_any_keyword(normalized_message, _FINANCIAL_KEYWORDS):
        return _build_transfer_decision(
            department_key="financial",
            department_catalog=department_catalog,
            reason="Assunto identificado como financeiro.",
        )

    if _contains_any_keyword(normalized_message, _SUPPORT_KEYWORDS):
        return _build_transfer_decision(
            department_key="support",
            department_catalog=department_catalog,
            reason="Assunto identificado como suporte tecnico.",
        )

    if qualification.is_ready_for_handoff:
        return _build_transfer_decision(
            department_key="sales",
            department_catalog=department_catalog,
            reason="Lead qualificado para transferencia comercial.",
        )

    return DepartmentTransferDecision(
        should_transfer=False,
        department_key=None,
        department_id=None,
        reason=None,
    )


def _build_transfer_decision(
    *,
    department_key: str,
    department_catalog: dict[str, str],
    reason: str,
) -> DepartmentTransferDecision:
    return DepartmentTransferDecision(
        should_transfer=True,
        department_key=department_key,
        department_id=department_catalog.get(department_key),
        reason=reason,
    )


def _resolve_intent(
    *,
    faq: FaqResolution | None,
    qualification: QualificationResult,
    transfer: DepartmentTransferDecision,
) -> IntentType:
    if transfer.should_transfer:
        return "transfer"
    if qualification.has_goal:
        return "qualification"
    if faq is not None:
        return "faq"
    return "general"


def _resolve_next_qualification_question(missing_fields: list[str]) -> str | None:
    if not missing_fields:
        return None

    next_field = missing_fields[0]
    if next_field == "goal":
        return "Para te direcionar corretamente, qual e o seu objetivo principal com esse atendimento?"
    if next_field == "budget":
        return "Voce ja tem uma faixa de investimento prevista para essa demanda?"
    return "Qual prazo voce gostaria de atender para essa demanda?"


def _contains_any_keyword(message: str, keywords: tuple[str, ...]) -> bool:
    for keyword in keywords:
        normalized_keyword = keyword.strip().lower()
        if not normalized_keyword:
            continue

        keyword_pattern = rf"(?<!\w){re.escape(normalized_keyword)}(?!\w)"
        if re.search(keyword_pattern, message):
            return True

    return False


def _normalize_message(value: str) -> str:
    without_spaces = value.strip().lower()
    if not without_spaces:
        return ""

    normalized = unicodedata.normalize("NFKD", without_spaces)
    return "".join(char for char in normalized if not unicodedata.combining(char))
