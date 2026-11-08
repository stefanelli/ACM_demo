"""Normalised quote observations.

One row per (contract, source) latest quote snapshot for the first increment.
This deliberately distinguishes event time, receive time, and ingestion time to
satisfy SPEC §6.2. A full event-history model will replace the "latest" approach
once the live/replay ingestion design is settled (SPEC §19).
"""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.contract import Contract


class Quote(Base):
    """Latest bid/ask/last snapshot for a contract from a single source."""

    __tablename__ = "quotes"
    __table_args__ = (
        Index("ix_quotes_contract_source", "contract_id", "source", unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    contract_id: Mapped[int] = mapped_column(
        ForeignKey("contracts.id", ondelete="CASCADE"), index=True
    )

    bid: Mapped[float | None] = mapped_column(Float, nullable=True)
    ask: Mapped[float | None] = mapped_column(Float, nullable=True)
    last: Mapped[float | None] = mapped_column(Float, nullable=True)

    source: Mapped[str] = mapped_column(String(32), default="mock")

    # Exchange event time, as reported by the source.
    event_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # Time the quote was received by the ingestion process.
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    contract: Mapped["Contract"] = relationship(back_populates="quotes")
