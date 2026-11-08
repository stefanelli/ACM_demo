"""Market-data service (MDS) domain types and source protocol.

The MDS is intended to be modular per the product direction: a pluggable
``MarketDataSource`` produces normalised observations, and downstream code does not
care whether they came from mock data, Databento backfill, or live replay.

This module defines the framing (no persistence): the "service" layer that persists
lives in ``app.mds.service``.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ContractSpec:
    """Normalised reference data for a single contract."""

    symbol: str
    name: str
    benchmark: str
    expiry_month: str
    settlement_style: str
    tick_value: float


@dataclass(frozen=True)
class MarketQuote:
    """Normalised market observation for a single contract snapshot."""

    symbol: str
    bid: float
    ask: float
    last: float
    source: str
    event_time: datetime


class MarketDataSource(ABC):
    """Pluggable source of market data.

    Implementations must return normalised ``ContractSpec`` / ``MarketQuote``
    objects independent of the underlying feed (mock, Databento, replay, ...).
    """

    @abstractmethod
    def list_contracts(self) -> list[ContractSpec]:
        """Return the contract universe available from this source."""

    @abstractmethod
    def latest_quotes(self) -> list[MarketQuote]:
        """Return the latest quote snapshot for each covered contract."""
