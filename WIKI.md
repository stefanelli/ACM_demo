# Aloe Wiki

A concise technical reference for the Fed meeting-curve research and paper-trading platform. See [SPEC.md](SPEC.md) for requirements and [JOURNAL.md](JOURNAL.md) for session handoff.

**Status:** design and Phase 0 verification; implementation has not started.

## 1. Purpose

Aloe will convert traded Fed interest-rate futures into a meeting-date SOFR curve, compare market expectations with an economist-approved house view, and evaluate outrights, calendar spreads, and butterflies after costs and portfolio risk.

```text
Market data → curve → house view → trade proposal → risk decision → backtest
```

The application must make rejections and uncertainty visible. A rate discrepancy is not automatically a trade.

## 2. Target implementation

- **Backend:** FastAPI services for market data, pricing, and research/risk; a separate backtest worker
- **Frontend:** React + TypeScript + Vite
- **Storage:** PostgreSQL for contracts, quotes, curves, views, trades, risk, and audit; Parquet for immutable raw data
- **Instruments:** SR1 and SR3 initially; SR3 is the primary liquidity source
- **Execution:** paper portfolio only
- **Deployment:** local Docker Compose; no Kubernetes, Kafka, or required cloud database
- **C++:** optional optimisation after Python profiling, not an initial requirement

Live and historical paths must use the same pricing, trade, cost, sizing, limit, and exit logic.

## 3. Futures mathematics

### Overnight path

Use published SOFR fixings where known and a piecewise-constant model path between scheduled Fed meetings. Unknown policy changes occur only at modelled meetings. Weekends and holidays inherit the preceding business-day rate with the correct accrual days.

### SR1

SR1 settles to `100 − R`, where `R` is the arithmetic average of daily SOFR during the delivery month:

\[
R_{arith}=\frac{\sum_i r_i\alpha_i}{\sum_i\alpha_i}
\]

Every calendar day receives a rate. Contract value: **$41.67/bp**.

### SR3

SR3 settles to `100 − R`, where `R` is daily SOFR compounded in arrears over the IMM reference quarter:

\[
A=\prod_i(1+r_i\alpha_i),\qquad
R_{comp}=\frac{A-1}{\sum_i\alpha_i}
\]

SOFR uses ACT/360. The quarter begins on the third Wednesday of the contract-name month and ends three months later. Contract value: **$25/bp**.

Exact exchange specifications and reference periods override generic calendar shortcuts.

### Curve calibration

Let \(x\) contain unknown policy changes at future meetings:

\[
\min_x \sum_j w_j\left(M_j(x)-P_j\right)^2+\lambda\Omega(x)
\]

- \(M_j(x)\): model futures price
- \(P_j\): observed futures price
- \(w_j\): liquidity, spread, and staleness weight
- \(\Omega(x)\): simple regularisation for under-identified paths

Report residuals, convergence, identification, data quality, and sensitivity to \(\lambda\). If several meeting paths fit, do not display one as uniquely determined.

## 4. House-view methodology

Keep three objects separate:

1. Market-implied expectations under the curve model
2. Economist-approved subjective scenario probabilities
3. Historical backtest results

A house view specifies meeting, allowed moves, prior probabilities, rationale, evidence, invalidators, author, version, and approval. Probabilities sum to one.

When evidence likelihoods are supplied, use:

\[
P(s\mid E)=\frac{P(s)\prod_kL_k(s)}{\sum_{s'}P(s')\prod_kL_k(s')}
\]

Without evidence likelihoods, label the output a subjective scenario view rather than a Bayesian update.

The LLM may challenge assumptions and suggest evidence or invalidators. It cannot fabricate data, approve a view, or authorise a trade. Historical tests cannot use retrospective LLM views informed by future outcomes.

## 5. Trade and risk methodology

### Proposal generation

Compare market and house expectations, then map the difference into:

- Outright futures
- Calendar spreads
- Meeting butterflies

Calculate actual contract weights using tick values, DV01 approximation, accrual sensitivity, and residual meeting exposures. A rate butterfly is not automatically a tradable futures butterfly.

### Expected edge

\[
\text{Net edge}=\sum_s p_sP\&L_s-\text{transaction costs}-\text{financing}-\text{capital hurdle}
\]

Every proposal includes scenario P&L, costs, liquidity, margin, stress loss, portfolio impact, entry tolerance, exit plan, and rejection reasons.

### Entry gates

Require an approved current view, positive net edge, acceptable curve residuals and identification, fresh liquid markets, acceptable price tolerance, and passing portfolio limits. No-trade is a valid result.

### Sizing

\[
N=\min\left(
\frac{R_{trade}}{L_{stress}},
\frac{D_{limit}}{|DV01_{trade}|},
N_{liquidity},
N_{margin}
\right)
\]

Round down to whole contracts and recompute multi-leg exposure. Show whether scenario loss, DV01, liquidity, or margin binds.

### Limits and exits

Use versioned limits for trade/meeting loss, gross/net DV01, concentration, correlated exposure, margin, daily/weekly loss, and drawdown.

Every position has a predefined exit plan:

- **Target:** market/house convergence
- **Thesis:** view changed or invalidated
- **Risk:** loss or exposure breach
- **Time:** meeting, expiry, roll, or holding limit
- **Market quality:** stale data or impaired liquidity

### Opportunity cost

Compare candidates using net P&L per unit of scenario loss and margin, correlation with current positions, capacity, holding period, and the value of preserving risk budget. Cash and competing trades are valid alternatives.

## 6. Backtesting methodology

- Use point-in-time contracts, calendars, fixings, quotes, views, and risk policies.
- Execute at the next eligible quote, not automatically at the signal quote.
- Model every leg, expiry, roll, cost, entry gate, size, limit, and exit.
- Use deterministic historical view rules or genuine previously recorded views.
- Report net performance, drawdown, expected shortfall, turnover, costs, capacity, no-trade frequency, regime breakdown, and cash/simple benchmarks.
- Reproduce each run from stored configuration and input hashes.

## 7. Assumptions

- Fed only in the initial release
- SR1/SR3 reference metadata and settlement formulas can be modelled exactly
- Scheduled meetings are the base event grid; unscheduled moves are scenario extensions
- Piecewise-constant overnight rates between meetings are an approximation
- Curve regularisation is explicit and configurable
- House probabilities are subjective, not automatically physical-world market probabilities
- DV01, margin, liquidity, and cost models are versioned approximations suitable for a POC
- Paper positions are sufficient; no production execution or accounting is claimed

## 8. Current limitations and blockers

- **No implementation refactor has started.**
- Databento historical access works for `SR1.FUT`, `SR3.FUT`, and `SR3.OPT`.
- Databento live access currently fails: `A live data license is required to access GLBX.MDP3.`
- Real-time operation therefore requires a live licence, another feed, or recorded-live replay.
- Bloomberg generic meeting-ticker import and point-in-time SOFR revision retrieval are unverified.
- Futures alone may not identify every meeting; ECB/BoE are out of scope.
- Options, cross-market curves, production execution, and full order-book ingestion are out of scope.
- Aggregate futures volume does not establish execution quality for every contract; bid/ask, depth, and staleness are still required.

## 9. Future work and extensions

1. **Forward-starting OIS:** 1M×1M, 3M×3M, and other pay/receive structures for targeted curve exposure. Pay fixed benefits from rising rates; receive fixed benefits from falling rates. Add counterparty/clearing, CSA/funding, collateral, valuation, and data-source requirements before treating these as executable alternatives to futures.
2. **Fed Funds futures:** separate EFFR path and SOFR/EFFR basis; do not substitute EFFR for SOFR.
3. **Options:** Black76, exact option/futures expiry mapping, implied-vol inversion, and volatility surfaces.
4. **Measured C++ optimisation:** accrual, batch scenario repricing, calibration, or replay only after profiling.
5. **Serialisation optimisation (msgspec):** the platform currently uses Pydantic v2 because it is FastAPI's native model/serialization layer and auto-generates OpenAPI schemas. `msgspec` is faster and lighter, and is a candidate for hot JSON paths (large quote/scenario payloads, high-throughput ingestion) *if* profiling shows serialization is a bottleneck. Apply it selectively (e.g. `msgspec.Struct` for the numeric core or `fastmsgspec` for specific endpoints) rather than replacing the Pydantic/OpenAPI layer wholesale.
6. **ECB and BoE:** €STR and SONIA curves, followed by cross-market relative value and correlation.
7. **ClickHouse:** only if actual tick-data scale and query benchmarks justify it.
8. **Execution research:** richer book-depth, slippage, roll, margin, and capacity models.

## 10. Documentation map

- [SPEC.md](SPEC.md): complete requirements, APIs, schemas, phases, and acceptance demonstration
- [JOURNAL.md](JOURNAL.md): current state, verified findings, blockers, and next actions
- [README.md](README.md): original application overview; will be updated when the refactor begins
