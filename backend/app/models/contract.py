"""Contract (instrument) reference data.

First slice: a minimal futures contract definition. This will grow as we add
reference periods, calendars, settlement formulas, and tick metadata per SPEC §6.1.
"""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Contract(Base):
    """A listed futures contract covered by the platform."""

    __tablename__ = "contracts"

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    # Benchmark/underlying rate: "SOFR" initially.
    benchmark: Mapped[str] = mapped_column(String(16))
    # Delivery/reference month for the contract (e.g. "2026-12").
    expiry_month: Mapped[str] = mapped_column(String(7))
    # Human-readable settlement style: "arith" (SR1) or "comp_arrears" (SR3).
    settlement_style: Mapped[str] = mapped_column(String(32))
    # Tick value in USD per basis point (SR1: 41.67, SR3: 25.00).
    tick_value: Mapped[float] = mapped_column()

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    quotes: Mapped[list["Quote"]] = relationship(back_populates="contract")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Contract {self.symbol} {self.expiry_month}>"
