"""Market-data API endpoints (versioned under /v1/market)."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db import get_db
from app.mds.service import refresh
from app.models import Contract, Quote
from app.schemas.market import (
    ContractOut,
    MarketHealthOut,
    QuoteOut,
    SyncResult,
)

router = APIRouter(prefix="/market", tags=["market"])


@router.get("/contracts", response_model=list[ContractOut])
def list_contracts(db: Session = Depends(get_db)) -> list[Contract]:
    """Return the full contract universe, ordered by symbol."""
    return list(db.scalars(select(Contract).order_by(Contract.symbol)))


@router.get("/quotes/latest", response_model=list[QuoteOut])
def latest_quotes(db: Session = Depends(get_db)) -> list[QuoteOut]:
    """Return the latest quote snapshot per contract, joined with the symbol."""
    rows = db.execute(
        select(Quote, Contract.symbol)
        .join(Contract, Quote.contract_id == Contract.id)
        .order_by(Contract.symbol)
    ).all()

    return [
        QuoteOut(
            symbol=symbol,
            bid=q.bid,
            ask=q.ask,
            last=q.last,
            source=q.source,
            event_time=q.event_time,
            received_at=q.received_at,
        )
        for q, symbol in rows
    ]


@router.get("/health", response_model=MarketHealthOut)
def market_health(db: Session = Depends(get_db)) -> MarketHealthOut:
    """Summarise data health for the market-data service."""
    contract_count = len(db.scalars(select(Contract.id)).all())
    quote_count = len(db.scalars(select(Quote.id)).all())

    return MarketHealthOut(
        status="ok",
        source=get_settings().mds_source,
        contract_count=contract_count,
        quote_count=quote_count,
        as_of=datetime.now(UTC),
    )


@router.post("/sync", response_model=SyncResult)
def sync_market_data(db: Session = Depends(get_db)) -> SyncResult:
    """Trigger a market-data refresh from the configured source."""
    n_contracts, n_quotes = refresh(db)
    return SyncResult(contracts=n_contracts, quotes=n_quotes)
