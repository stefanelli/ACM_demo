"""Databento market-data source (stub).

Placeholder for the real adapter. Implemented later against the ``MarketDataSource``
protocol once the live-feed strategy is chosen (SPEC §19). Historical backfill uses
the same interface, so no call-site changes are required downstream.
"""

from app.mds.base import ContractSpec, MarketDataSource, MarketQuote


class DatabentoSource(MarketDataSource):
    """Not yet implemented — see JOURNAL.md current blocker."""

    def __init__(self) -> None:
        raise NotImplementedError(
            "Databento live access requires a live licence: "
            "see JOURNAL.md 'Current blocker'."
        )

    def list_contracts(self) -> list[ContractSpec]:  # pragma: no cover
        raise NotImplementedError

    def latest_quotes(self) -> list[MarketQuote]:  # pragma: no cover
        raise NotImplementedError
