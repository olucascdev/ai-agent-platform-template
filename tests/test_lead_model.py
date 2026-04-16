"""Testes estruturais do modelo `Lead`."""

from sqlalchemy import Table, UniqueConstraint

from db.models import Lead


def test_lead_table_name_is_leads() -> None:
    """Garante que o modelo aponta para a tabela esperada pela migration."""
    assert Lead.__tablename__ == "leads"


def test_lead_has_unique_constraint_for_phone() -> None:
    """Valida unicidade de telefone para evitar duplicacao de lead."""
    lead_table = Lead.__table__
    assert isinstance(lead_table, Table)

    unique_constraints = [
        constraint for constraint in lead_table.constraints if isinstance(constraint, UniqueConstraint)
    ]

    assert any(constraint.name == "uq_leads_phone" for constraint in unique_constraints)


def test_lead_columns_match_phase_contract() -> None:
    """Confere colunas obrigatorias previstas no contrato da Fase 3."""
    column_names = set(Lead.__table__.columns.keys())

    assert column_names == {
        "id",
        "phone",
        "session_id",
        "crm_contact_id",
        "created_at",
        "updated_at",
    }

    assert Lead.__table__.columns["phone"].nullable is False
    assert Lead.__table__.columns["session_id"].nullable is False
