import { useEffect, useState } from "react";
import { api, type MarketHealth, type Quote } from "../api/client";

function formatTime(iso: string | null): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleTimeString();
}

export default function MarketHealth() {
  const [health, setHealth] = useState<MarketHealth | null>(null);
  const [quotes, setQuotes] = useState<Quote[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    const load = async () => {
      try {
        const [h, q] = await Promise.all([
          api.marketHealth(),
          api.latestQuotes(),
        ]);
        if (active) {
          setHealth(h);
          setQuotes(q);
        }
      } catch (e) {
        if (active) setError(e instanceof Error ? e.message : String(e));
      }
    };
    load();
    return () => {
      active = false;
    };
  }, []);

  if (error) {
    return <div className="error">Failed to load market data: {error}</div>;
  }

  if (!health) {
    return <div className="muted">Loading…</div>;
  }

  return (
    <section>
      <h2>Market health</h2>
      <p>
        Source: <strong>{health.source}</strong>{" "}
        <span className="badge badge-ok">{health.status}</span>
      </p>

      <table>
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Bid</th>
            <th>Ask</th>
            <th>Last</th>
            <th>Event time</th>
          </tr>
        </thead>
        <tbody>
          {quotes.map((q) => (
            <tr key={q.symbol}>
              <td>{q.symbol}</td>
              <td>{q.bid?.toFixed(4) ?? "—"}</td>
              <td>{q.ask?.toFixed(4) ?? "—"}</td>
              <td>{q.last?.toFixed(4) ?? "—"}</td>
              <td>{formatTime(q.event_time)}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <p className="muted">
        {health.contract_count} contracts · {health.quote_count} quotes · as of{" "}
        {formatTime(health.as_of)}
      </p>
    </section>
  );
}
