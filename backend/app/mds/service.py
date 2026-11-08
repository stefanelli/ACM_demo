"""MDS service: select a source and persist normalised data into Postgres.

This is the thin orchestration layer the API and CLI use. It holds no market
logic — it just routes between a ``MarketDataSource`` and the database.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.mds.base import MarketDataSource, MarketQuote
from app.mds.databento_source import DatabentoSource
from app.mds.mock_source import MockMarketDataSource
from app.models import Contract, Quote


def build_source() -> MarketDataSource:
    """Instantiate the configured market-data source."""
    source_name = get_settings().mds_source
    if source_name == "mock":
        return MockMarketDataSource()
    if source_name == "databento":
        return DatabentoSource()
    raise ValueError(f"Unknown MDS source: {source_name!r}")


def sync_contracts(session: Session, source: MarketDataSource) -> int:
    """Upsert the source's contract universe and return the count.

    Idempotent: existing contracts (by symbol) are updated in place.
    """
    count = 0
    for spec in source.list_contracts():
        contract = session.scalar(
            select(Contract).where(Contract.symbol == spec.symbol)
        )
        if contract is None:
            contract = Contract(symbol=spec.symbol)
            session.add(contract)
        contract.name = spec.name
        contract.benchmark = spec.benchmark
        contract.expiry_month = spec.expiry_month
        contract.settlement_style = spec.settlement_style
        contract.tick_value = spec.tick_value
        count += 1
    session.commit()
    return count


def sync_quotes(session: Session, source: MarketDataSource) -> int:
    """Persist the source's latest quotes and return the count.

    Idempotent: the unique (contract, source) pair is updated in place so repeated
    calls only refresh the latest snapshot.
    """
    symbols = {c.symbol: c.id for c in session.scalars(select(Contract)).all()}

    count = 0
    for q in source.latest_quotes():
        contract_id = symbols.get(q.symbol)
        if contract_id is None:
            raise ValueError(f"Quote references unknown contract: {q.symbol!r}")

        quote = session.scalar(
            select(Quote).where(
                Quote.contract_id == contract_id, Quote.source == q.source
            )
        )
        if quote is None:
            quote = Quote(contract_id=contract_id, source=q.source)
            session.add(quote)
        quote.bid = q.bid
        quote.ask = q.ask
        quote.last = q.last
        quote.event_time = q.event_time
        count += 1
    session.commit()
    return count


def refresh(session: Session) -> tuple[int, int]:
    """Run a full sync: contracts then quotes. Returns (contracts, quotes) counts."""
    source = build_source()
    n_contracts = sync_contracts(session, source)
    n_quotes = sync_quotes(session, source)
    return n_contracts, n_quotes
