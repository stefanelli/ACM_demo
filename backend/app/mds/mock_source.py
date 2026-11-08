"""Mock market-data source used for the first development increment.

Produces deterministic, plausible SR1/SR3 quotes so the full pipeline (MDS ->
Postgres -> API -> UI) can be exercised without a live feed. This is intentionally
simple: the real Databento adapter will implement the same ``MarketDataSource``
protocol in ``databento_source.py``.
"""

import random
from datetime import UTC, datetime

from app.mds.base import ContractSpec, MarketDataSource, MarketQuote

# A small universe of SR1 (1-month) and SR3 (3-month) SOFR futures.
_CONTRACTS: list[ContractSpec] = [
    ContractSpec(
        symbol="SR1Z6",
        name="One-Month SOFR Futures Dec 2026",
        benchmark="SOFR",
        expiry_month="2026-12",
        settlement_style="arith",
        tick_value=41.67,
    ),
    ContractSpec(
        symbol="SR1F7",
        name="One-Month SOFR Futures Jan 2027",
        benchmark="SOFR",
        expiry_month="2027-01",
        settlement_style="arith",
        tick_value=41.67,
    ),
    ContractSpec(
        symbol="SR3Z6",
        name="Three-Month SOFR Futures Dec 2026",
        benchmark="SOFR",
        expiry_month="2026-12",
        settlement_style="comp_arrears",
        tick_value=25.00,
    ),
    ContractSpec(
        symbol="SR3H7",
        name="Three-Month SOFR Futures Mar 2027",
        benchmark="SOFR",
        expiry_month="2027-03",
        settlement_style="comp_arrears",
        tick_value=25.00,
    ),
]


class MockMarketDataSource(MarketDataSource):
    """Deterministic mock source with optional seed for reproducible quotes."""

    def __init__(self, seed: int | None = 42) -> None:
        self._rng = random.Random(seed)

    def list_contracts(self) -> list[ContractSpec]:
        return list(_CONTRACTS)

    def latest_quotes(self) -> list[MarketQuote]:
        """Generate a plausible quote snapshot for each contract.

        Prices are built around a base level of 96.0 (i.e. ~4% implied rate) with
        a small deterministic spread so bid <= last <= ask always holds.
        """
        now = datetime.now(UTC)
        quotes: list[MarketQuote] = []
        for spec in _CONTRACTS:
            mid = 96.0 + self._rng.uniform(-0.25, 0.25)
            spread = 0.005 + self._rng.uniform(0.0, 0.01)
            bid = round(mid - spread / 2, 4)
            ask = round(mid + spread / 2, 4)
            last = round((bid + ask) / 2, 4)
            quotes.append(
                MarketQuote(
                    symbol=spec.symbol,
                    bid=bid,
                    ask=ask,
                    last=last,
                    source="mock",
                    event_time=now,
                )
            )
        return quotes
