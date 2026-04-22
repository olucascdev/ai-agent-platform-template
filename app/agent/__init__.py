"""Utilitarios de orquestracao do agente conversacional."""

from app.agent.conversation_rules import (
    DEFAULT_DEPARTMENT_IDS,
    ConversationRulesDecision,
    DepartmentTransferDecision,
    FaqResolution,
    IntentType,
    QualificationResult,
    evaluate_conversation_rules,
)
from app.agent.factory import (
    DEFAULT_AGENT_MODEL_ID,
    DEFAULT_AGENT_MODEL_PROVIDER,
    DEFAULT_CLAUDE_MODEL_ID,
    DEFAULT_CLAUDE_OPENROUTER_MODEL_ID,
    DEFAULT_GEMINI_MODEL_ID,
    DEFAULT_GROQ_MODEL_ID,
    DEFAULT_OPENROUTER_MODEL_ID,
    SUPPORTED_AGENT_MODEL_PROVIDERS,
    AgentFactory,
    build_agent_factory,
    build_default_agent_model,
    build_default_openai_model,
)
from app.agent.guardrails import (
    DEFAULT_GUARDRAIL_FALLBACK_TEXT,
    GuardrailResult,
    GuardrailViolation,
    apply_response_guardrails,
)
from app.agent.handoff_comments import HandoffCommentInput, build_structured_handoff_comment
from app.agent.runtime_context import build_runtime_context_block, compose_message_with_runtime_context
from app.agent.session import build_single_client_session_id

__all__ = [
    "AgentFactory",
    "ConversationRulesDecision",
    "DEFAULT_DEPARTMENT_IDS",
    "DEFAULT_AGENT_MODEL_ID",
    "DEFAULT_AGENT_MODEL_PROVIDER",
    "DEFAULT_CLAUDE_MODEL_ID",
    "DEFAULT_CLAUDE_OPENROUTER_MODEL_ID",
    "DEFAULT_GEMINI_MODEL_ID",
    "DEFAULT_GUARDRAIL_FALLBACK_TEXT",
    "DEFAULT_GROQ_MODEL_ID",
    "DEFAULT_OPENROUTER_MODEL_ID",
    "DepartmentTransferDecision",
    "FaqResolution",
    "GuardrailResult",
    "GuardrailViolation",
    "HandoffCommentInput",
    "IntentType",
    "QualificationResult",
    "SUPPORTED_AGENT_MODEL_PROVIDERS",
    "apply_response_guardrails",
    "build_agent_factory",
    "build_default_agent_model",
    "build_runtime_context_block",
    "compose_message_with_runtime_context",
    "build_structured_handoff_comment",
    "evaluate_conversation_rules",
    "build_single_client_session_id",
    "build_default_openai_model",
]
