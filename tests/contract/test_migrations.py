"""Offline migration compilation proves revisions are ordered and renderable."""

from alembic import command
from alembic.config import Config


def test_alembic_head_renders_postgresql_sql() -> None:
    config = Config("alembic.ini")
    command.upgrade(config, "head", sql=True)
