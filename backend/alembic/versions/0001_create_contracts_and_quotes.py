"""create contracts and quotes tables

Revision ID: 0001
Revises:
Create Date: 2026-11-08

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "contracts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("benchmark", sa.String(length=16), nullable=False),
        sa.Column("expiry_month", sa.String(length=7), nullable=False),
        sa.Column("settlement_style", sa.String(length=32), nullable=False),
        sa.Column("tick_value", sa.Float(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_contracts_symbol", "contracts", ["symbol"], unique=True)

    op.create_table(
        "quotes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "contract_id",
            sa.Integer(),
            sa.ForeignKey("contracts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("bid", sa.Float(), nullable=True),
        sa.Column("ask", sa.Float(), nullable=True),
        sa.Column("last", sa.Float(), nullable=True),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("event_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "received_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_quotes_contract_id", "quotes", ["contract_id"])
    op.create_index(
        "ix_quotes_contract_source",
        "quotes",
        ["contract_id", "source"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_quotes_contract_source", table_name="quotes")
    op.drop_index("ix_quotes_contract_id", table_name="quotes")
    op.drop_table("quotes")
    op.drop_index("ix_contracts_symbol", table_name="contracts")
    op.drop_table("contracts")
