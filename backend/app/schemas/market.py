"""Pydantic response schemas for the market-data API."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ContractOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    symbol: str
    name: str
    benchmark: str
    expiry_month: str
    settlement_style: str
    tick_value: float


class QuoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    symbol: str
    bid: float | None
    ask: float | None
    last: float | None
    source: str
    event_time: datetime | None
    received_at: datetime


class MarketHealthOut(BaseModel):
    status: str
    source: str
    contract_count: int
    quote_count: int
    as_of: datetime


class SyncResult(BaseModel):
    contracts: int
    quotes: int
