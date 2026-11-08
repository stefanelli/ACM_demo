export interface Contract {
  id: number;
  symbol: string;
  name: string;
  benchmark: string;
  expiry_month: string;
  settlement_style: string;
  tick_value: number;
}

export interface Quote {
  symbol: string;
  bid: number | null;
  ask: number | null;
  last: number | null;
  source: string;
  event_time: string | null;
  received_at: string;
}

export interface MarketHealth {
  status: string;
  source: string;
  contract_count: number;
  quote_count: number;
  as_of: string;
}

const BASE = "";

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  contracts: () => get<Contract[]>("/v1/market/contracts"),
  latestQuotes: () => get<Quote[]>("/v1/market/quotes/latest"),
  marketHealth: () => get<MarketHealth>("/v1/market/health"),
};
