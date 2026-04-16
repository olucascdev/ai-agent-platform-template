"""Base declarativa do SQLAlchemy para os modelos da aplicacao."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Classe base para mapear tabelas do projeto."""
