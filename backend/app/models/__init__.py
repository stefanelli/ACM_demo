"""ORM models registry.

Importing this module makes every model known to SQLAlchemy's metadata, which is
required for `Base.metadata.create_all` and Alembic autogenerate to see all tables.
"""

from app.models.contract import Contract
from app.models.quote import Quote

__all__ = ["Contract", "Quote"]
