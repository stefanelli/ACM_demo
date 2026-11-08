# Aloe — Fed Meeting-Curve Research and Risk Platform

**Status:** Proposed for implementation  
**Date:** 2026-11-07  
**Initial scope:** Federal Reserve, listed interest-rate futures, paper trading only

## 1. Purpose

Aloe is a real-time research and risk platform that converts listed Fed interest-rate futures into a defensible meeting-date policy curve, compares that curve with an economist-approved house view, and evaluates tradeable opportunities under explicit portfolio-risk constraints.

The complete workflow is:

```text
Live futures and reference data
        ↓
Meeting-date RFR curve with calibration diagnostics
        ↓
Market-implied expectations versus approved house view
        ↓
Outright, calendar-spread, and butterfly proposals
        ↓
Entry gates, sizing, limits, exits, and opportunity-cost analysis
        ↓
Paper portfolio and point-in-time backtesting
```

The application must demonstrate both:

- **Quantitative development:** live ingestion, typed service APIs, data lineage, numerical pricing, storage, resilience, and measured performance.
- **Quantitative research:** interest-rate futures knowledge, RFR accrual, curve identification, subjective Bayesian scenario analysis, trade construction, and risk-adjusted evaluation.

## 2. Product principles

1. **The futures are the market data.** Bloomberg generic meeting tickers and official calendars define the event grid; they do not replace traded prices.
2. **No false precision.** If futures do not uniquely identify a meeting path, the application exposes regularisation and sensitivity rather than hiding the problem.
3. **One numerical implementation.** Live pricing, research, and backtesting use the same curve, trade, cost, and risk logic.
4. **Risk is central.** A proposal cannot enter the paper portfolio without passing the risk engine.
5. **No-trade is a valid result.** Positive headline mispricing is insufficient when costs, downside, capital use, or portfolio concentration are unattractive.
6. **Small services, not distributed complexity.** Use a few typed deployable services and avoid Kafka, Kubernetes, and premature infrastructure.
7. **C++ must earn its place.** Build a clear Python reference first; optimise only measured hot paths.
8. **The LLM assists, never authorises.** An economist approves every house view and trade decision.

## 3. Scope

### 3.1 Initial release

- Federal Reserve only
- SR1 and SR3 futures as the initial instrument universe
- Databento live quotes and historical backfill, subject to dataset and entitlement verification
- Published SOFR fixings and Fed meeting calendars
- Meeting-date curve calibration and diagnostics
- Economist-authored discrete cut/hold/hike scenarios with optional Bayesian evidence updates
- LLM-assisted formulation and challenge of house views
- Outrights, calendar spreads, and meeting butterflies
- Scenario P&L, transaction costs, sizing, limits, exits, and opportunity costs
- Paper portfolio and deterministic backtesting
- FastAPI backend services and React + TypeScript frontend
- PostgreSQL system of record and Parquet raw-data storage

### 3.2 Explicit non-goals for the initial release

- ECB, BoE, or cross-market curves
- Options and volatility-surface calibration
- Real broker order routing
- Full order-book or multi-year tick-data ingestion
- A generic long-maturity yield-curve application
- Fully autonomous LLM research or trading
- Production PM, accounting, or compliance functionality
- Kubernetes, Kafka, or multi-region deployment

### 3.3 Later extensions

- Fed Funds futures, modelled with a distinct EFFR path and SOFR/EFFR basis rather than assuming the benchmarks are identical
- Futures options using Black76, exact option/futures expiry mapping, and implied-volatility surfaces
- C++ event replay or additional numerical optimisation
- ECB and BoE meeting curves and cross-market relative value
- ClickHouse for event data if measured scale requires it

## 4. User workflows

### 4.1 Economist

1. Inspect current market-implied meeting expectations and data quality.
2. Create a cut/hold/hike prior for a specified meeting.
3. Ask the LLM assistant to challenge assumptions, identify evidence, and propose invalidators.
4. Review evidence and optionally assign likelihood ratios for a Bayesian update.
5. Edit and approve the resulting house view.
6. Compare the approved view with the market curve.

### 4.2 Researcher

1. Inspect candidate outrights, spreads, and butterflies.
2. Compare expected net edge, downside, margin use, and opportunity cost.
3. Run the pre-trade risk assessment.
4. Enter approved trades into the paper portfolio.
5. Monitor convergence, thesis invalidation, limits, and exits.
6. Review historical performance using the same decision and risk rules.

### 4.3 Developer/operator

1. Monitor ingestion, quote freshness, rejected records, and service health.
2. Backfill historical data without duplicating records.
3. Reproduce any curve, trade, or risk decision from its stored inputs and configuration.
4. Profile numerical workloads and optimise only demonstrated bottlenecks.

## 5. Architecture

```text
                         ┌────────────────────────┐
Databento ──────────────►│ Market-data service    │
                         │ live + backfill + QA   │
                         └───────────┬────────────┘
                                     │
                        PostgreSQL + Parquet storage
                                     │
              ┌──────────────────────┼──────────────────────┐
              ▼                      ▼                      ▼
   ┌────────────────────┐ ┌────────────────────┐ ┌────────────────────┐
   │ Pricing service    │ │ Research/risk      │ │ Backtest worker    │
   │ FastAPI            │ │ FastAPI + LLM      │ │ same domain logic  │
   │ optional C++ core  │ │ trade + portfolio  │ │ historical runs    │
   └─────────┬──────────┘ └─────────┬──────────┘ └─────────┬──────────┘
             │                    │                      │
             └────────────────────┼──────────────────────┘
                                  ▼
                    React + TypeScript frontend
```

### 5.1 Market-data service

Responsibilities:

- Databento live subscription and historical backfill
- Contract and symbol normalisation
- Immutable raw-event capture
- Quote persistence and publication to downstream consumers
- Reconnection, sequence-gap detection, and stale-data reporting
- Ingestion audit and idempotency

Reference data such as meeting calendars and fixings may use scheduled polling even when futures quotes use streaming delivery.

### 5.2 Pricing service

Responsibilities:

- Contract reference-period and settlement calculations
- SOFR accrual and futures-price calculations
- Meeting-curve calibration
- Residual, sensitivity, and identification diagnostics
- Scenario repricing for trade evaluation
- Optional C++ numerical core behind the same Python-facing interface

### 5.3 Research and risk service

Responsibilities:

- House-view creation, evidence updates, approval, and versioning
- LLM dialogue and structured-output validation
- Market-versus-house comparison
- Trade construction and scenario P&L
- Entry gates, sizing, limits, exits, and opportunity costs
- Paper positions, cash/ledger entries, and portfolio exposure
- Backtest orchestration through a worker using the same domain libraries

### 5.4 Frontend

Use React + TypeScript + Vite. Dash is excluded.

- Use REST for request/response workflows.
- Use a lightweight streaming mechanism for live quote and curve updates where useful.
- Generate TypeScript API types from FastAPI OpenAPI schemas.
- Keep presentation logic out of pricing and risk services.

### 5.5 Deployment

- Local development through Docker Compose
- Environment-specific configuration through environment variables
- Versioned JSON APIs under `/v1`
- Health endpoints and structured logs for every service
- No secrets in source, notebooks, frontend code, or committed data files

## 6. Data specification

### 6.1 Reference data

Store versioned definitions for:

- Venue and instrument
- Contract symbol and expiry
- Futures reference-period start and end
- Price quotation, tick size, and tick value
- Settlement formula and benchmark
- Day-count and holiday calendar
- Fed meeting dates and publication times where relevant
- SOFR fixings with observation and publication timestamps

Bloomberg generic meeting tickers may be used as an import source when available. The application must also support a versioned local calendar input so development is not blocked by a Bloomberg dependency.

### 6.2 Market observations

Each observation records:

- Contract and source
- Event timestamp and receive timestamp in UTC
- Bid, ask, last, and settlement where available
- Bid/ask sizes where available
- Sequence and ingestion-run identifiers
- Raw/normalised schema versions

Preserve the distinction between event time, receive time, and ingestion time.

### 6.3 Storage

PostgreSQL stores:

- Contracts and meeting calendars
- Fixings and normalised quotes
- Curves and calibration diagnostics
- House views and evidence
- Trade proposals and risk assessments
- Risk policies and limits
- Paper positions and ledger entries
- Backtest definitions and results
- Ingestion and processing runs

Parquet stores immutable raw Databento extracts and larger event samples, partitioned by dataset, date, venue, and instrument as appropriate.

All ingestion must be idempotent using natural keys, source identifiers, and/or input hashes.

### 6.4 Data-quality gates

Track and expose:

- Stale quotes
- Crossed or invalid markets
- Abnormal bid/ask spreads
- Missing reference periods or calendars
- Sequence gaps and reconnects
- Duplicate records
- Insufficient contract coverage
- Contracts approaching expiry or roll

A curve or trade built from unhealthy data must carry a visible warning and may be rejected by the risk engine.

## 7. Futures and RFR pricing

### 7.1 Overnight-rate path

For each day \(i\), let \(r_i\) be the overnight SOFR rate and \(\alpha_i\) its accrual fraction using ACT/360 and the relevant calendar.

The path consists of:

1. Published fixings for historical observations
2. Piecewise-constant model rates between scheduled Fed meetings
3. Unknown policy-rate changes at future meetings

Unscheduled meetings and large unexpected intra-meeting moves are scenario extensions, not assumptions in the base curve.

### 7.2 Contract calculations

For an arithmetic-average contract:

\[
R_{arith}=\frac{\sum_i r_i\alpha_i}{\sum_i\alpha_i}
\]

For a compounded contract:

\[
A=\prod_i(1+r_i\alpha_i)
\]

\[
R_{comp}=\frac{A-1}{\sum_i\alpha_i}
\]

The quoted futures price is represented as \(100-R\), with units handled explicitly in implementation.

SR1 monthly averaging and SR3 quarterly compounding must follow their exact exchange specifications. Contract code must not assume that a reference period ends on the futures expiry date without validating the contract rules.

### 7.3 Numerical correctness

Before optimisation, validate simple examples:

- Constant overnight rate reproduces the expected arithmetic and compounded rates.
- Accrual over weekends and holidays uses the correct day weights.
- A one-meeting change affects only the intended reference periods.
- Model prices are invariant to harmless input reordering.
- Python and any later C++ implementation agree within a documented numerical tolerance.

## 8. Meeting-curve calibration

### 8.1 State

The state vector \(x\) contains unknown policy changes at selected future meetings. Rates before the first modelled meeting and after the final covered meeting require explicit boundary assumptions.

### 8.2 Objective

Calibrate using:

\[
\min_x \sum_j w_j\left(M_j(x)-P_j\right)^2 + \lambda\Omega(x)
\]

Where:

- \(M_j(x)\): model futures price
- \(P_j\): market mid, settlement, or other documented observation
- \(w_j\): weight based on liquidity, bid/ask width, and staleness
- \(\Omega(x)\): regularisation for under-identified meeting paths
- \(\lambda\): versioned calibration parameter

The initial regulariser should be simple and explainable, such as penalising unnecessary variation between adjacent meeting changes. Do not introduce a complex prior solely to make the curve appear smooth.

### 8.3 Outputs

Each `CurveSnapshot` contains:

- As-of timestamp and input identifiers
- Expected change at each meeting
- Cumulative expected policy path
- Model and observed price for every futures contract
- Residuals in price and basis-point terms
- Calibration settings and convergence status
- Identification and sensitivity warnings
- Data-quality warnings

### 8.4 Required diagnostics

- Number and condition of independent pricing constraints
- Residual by contract
- Sensitivity to \(\lambda\)
- Sensitivity to reasonable alternative meeting assumptions
- Meetings weakly covered by the instrument universe
- Changes in the curve caused by individual quote updates

If multiple materially different paths fit the market, the UI must not present one as uniquely determined.

## 9. House views and Bayesian analysis

### 9.1 Separate objects

The system must keep separate:

1. Market-implied expectations under the curve model
2. Economist-approved subjective house-view probabilities
3. Historical backtest statistics

A difference between the first two is a relative-value assessment, not proof of risk-free arbitrage.

### 9.2 Scenario schema

Each house view contains:

- Meeting and forecast horizon
- Allowed policy moves in basis points
- Prior probability for every scenario
- Evidence items and sources
- Optional scenario likelihoods or likelihood ratios
- Rationale and invalidators
- Confidence and assumptions
- Author, timestamps, version, and approval status

Probabilities must sum to one and policy moves must use configured increments.

### 9.3 Bayesian update

When evidence likelihoods are supplied:

\[
P(s\mid E)=\frac{P(s)\prod_k L_k(s)}{\sum_{s'}P(s')\prod_k L_k(s')}
\]

Evidence weights or likelihood tempering may be used for correlated or subjective evidence. Dependencies between evidence items must be visible.

If the economist directly supplies only a scenario distribution without evidence likelihoods, label it a **subjective scenario view**, not a Bayesian update.

### 9.4 LLM assistant

The assistant may:

- Ask clarifying questions
- Summarise economist-provided evidence
- Propose scenario rationales and invalidators
- Identify correlated evidence and missing assumptions
- Suggest likelihood ratios for economist review
- Compare a new view with earlier approved views

The assistant may not:

- Fabricate economic observations or citations
- Approve a house view
- Change probabilities without showing the change
- Directly authorise or enter a trade

Historical backtests must not use retrospective LLM views formed with future knowledge. Use deterministic point-in-time rules or views actually recorded before the relevant market outcome.

## 10. Trade generation

### 10.1 Supported structures

- Outright futures position
- Calendar spread
- Meeting butterfly

For each structure, calculate contract weights using the relevant tick values, DV01 approximation, accrual sensitivity, and residual meeting exposures. A rate butterfly is not automatically a tradable futures butterfly.

### 10.2 Trade proposal

Every proposal includes:

- Instrument legs, direction, and weights
- Market-implied and house-view expectations
- Expected P&L under every scenario
- Carry and roll-down where meaningful
- Transaction, slippage, and financing costs
- Margin and capital consumption
- Stress loss and residual curve-model exposure
- Liquidity and staleness
- Entry conditions and allowed price tolerance
- Proposed size and binding sizing constraint
- Portfolio impact and correlated positions
- Opportunity-cost metrics
- Exit plan
- Approval or rejection reasons

### 10.3 Expected edge

\[
\text{Net expected edge}
=
\sum_s p_s P\&L_s
-\text{transaction costs}
-\text{financing costs}
-\text{capital hurdle}
\]

The capital hurdle uses margin consumed, expected holding time, and a cash/RFR benchmark.

## 11. Risk management

### 11.1 Entry gates

A trade may enter only if all applicable gates pass:

- House view approved and current
- Positive expected net edge
- Edge exceeds configured minimum after all costs
- Curve residuals and identification within tolerance
- Quotes fresh and liquidity acceptable
- Price remains within entry tolerance
- No incompatible duplicate exposure
- Meeting, contract, DV01, margin, and concentration limits pass
- Daily-loss, drawdown, and global kill switches inactive

Every rejection returns explicit failed conditions.

### 11.2 Scenario-based sizing

For a candidate trade:

\[
N=\min\left(
\frac{R_{trade}}{L_{stress}},
\frac{D_{limit}}{|DV01_{trade}|},
N_{liquidity},
N_{margin}
\right)
\]

Where \(R_{trade}\) is the allocated scenario-loss budget and \(L_{stress}\) is the defined stress loss per contract.

Round down to whole contracts and recompute all legs and portfolio exposures. Display whether scenario loss, DV01, liquidity, or margin determined the final size.

Stress cases include:

- House view wrong in each adverse direction
- Gap to an alternative policy path
- Butterfly residual exposure
- Wider exit bid/ask
- Increased correlation
- Existing positions experiencing the same scenario

### 11.3 Risk policy

Versioned limits include:

- Maximum loss per trade and per meeting
- Gross and net DV01
- Contract and butterfly concentration
- Correlated-theme exposure
- Margin utilisation
- Daily and weekly loss
- Portfolio drawdown
- Minimum liquidity and maximum bid/ask
- Global kill switch

### 11.4 Exit rules

Every position has an `ExitPlan` created before entry. Supported exits:

1. **Target:** sufficient market/house convergence
2. **Thesis:** view changed, withdrawn, or invalidated
3. **Risk:** loss, exposure, or drawdown limit breached
4. **Time:** meeting, expiry, roll, or maximum holding period approached
5. **Market quality:** liquidity or data integrity deteriorated

Every exit records timestamp, trigger, market state, and resulting ledger entries.

### 11.5 Opportunity cost

Rank candidates under common capital and risk budgets using:

- Expected net P&L per unit of scenario loss
- Expected net P&L per unit of margin
- Correlation with current positions
- Holding period
- Liquidity and capacity
- Cost as a share of expected edge
- Value of preserving risk budget for future opportunities

Cash and competing proposals are valid alternatives. A positive-edge trade may be rejected when a better use of the same risk budget exists.

## 12. Backtesting

### 12.1 Rules

- Use point-in-time contracts, calendars, fixings, quotes, and risk policies.
- Form signals using only information available at that timestamp.
- Execute at the next eligible quote, not the signal quote by assumption.
- Apply entry gates, sizing, limits, exits, and costs identically to live evaluation.
- Model every leg, roll, expiry, and transaction cost.
- Use deterministic historical view rules or genuine previously recorded views.
- Do not optimise on the full sample and report the result as out-of-sample evidence.

### 12.2 Backtester implementation

Evaluate an existing backtest accounting library before building one. Curve construction, signal generation, futures mapping, and risk logic remain Aloe domain code regardless of the accounting library selected.

If the library obscures rolls, multi-leg positions, or risk semantics, use a small explicit ledger instead.

### 12.3 Outputs

- Gross and net performance
- Return on margin and scenario-risk budget
- Maximum drawdown and expected shortfall
- Turnover and transaction-cost share
- Capacity and liquidity diagnostics
- No-trade frequency
- Results by policy cycle and volatility regime
- Cash and simple-strategy benchmarks
- Cost and risk-limit sensitivity
- Reproducible configuration and input hashes

## 13. API outline

All APIs are versioned and return an `as_of` timestamp where relevant.

### Market data

- `GET /v1/market/contracts`
- `GET /v1/market/quotes/latest`
- `GET /v1/market/health`
- `POST /v1/market/backfill`

### Pricing

- `POST /v1/curves/calibrate`
- `GET /v1/curves/latest`
- `GET /v1/curves/{curve_id}`
- `POST /v1/pricing/scenarios`

### House views and research

- `POST /v1/views`
- `POST /v1/views/{view_id}/evidence`
- `POST /v1/views/{view_id}/approve`
- `POST /v1/trades/evaluate`
- `GET /v1/trades/proposals`

### Risk and portfolio

- `POST /v1/risk/precheck`
- `GET /v1/risk/exposure`
- `GET /v1/risk/limits`
- `POST /v1/positions/paper-entry`
- `POST /v1/positions/{position_id}/exit`

### Backtesting

- `POST /v1/backtests`
- `GET /v1/backtests/{run_id}`

Write operations are asynchronous when they exceed normal request latency. Job status and input identifiers must be persisted.

## 14. Frontend screens

1. **Market health:** live futures, bid/ask, freshness, ingestion and contract coverage.
2. **Curve:** meeting expectations, cumulative policy path, futures residuals, and calibration sensitivity.
3. **House view:** scenario editor, LLM assistant, evidence, Bayesian update, and approval history.
4. **Trade ideas:** candidate ranking, expected edge, scenario P&L, costs, and opportunity-cost comparison.
5. **Risk and portfolio:** sizing, binding constraints, limits, exposures, open positions, and exits.
6. **Backtest:** configuration, reproducibility, results, costs, and risk diagnostics.

The UI must distinguish live data, replayed data, and historical backtests.

## 15. C++ decision framework

### 15.1 Candidates

- RFR accrual and futures settlement
- Batch scenario repricing
- Repeated curve calibration
- Event replay if later required

### 15.2 Adoption requirements

C++ is introduced only when:

- A Python reference implementation exists and is validated.
- Profiling identifies a material bottleneck.
- The expected speedup justifies additional build and interface complexity.
- The C++ implementation matches Python within a documented tolerance.
- Live pricing and backtesting can call the same numerical core.

If these conditions are not met, retain Python and document the decision.

## 16. Non-functional requirements

- **Reproducibility:** every curve, view, trade, risk decision, and backtest stores inputs, configuration, timestamps, and code/schema versions.
- **Auditability:** approvals, overrides, entries, and exits are append-only where practical.
- **Resilience:** live ingestion reconnects and reports gaps; stale data does not silently produce trusted trades.
- **Security:** API keys remain server-side and are never committed.
- **Simplicity:** a new developer can run the Fed vertical slice locally without Bloomberg, Databricks, Kubernetes, or a cloud database.
- **Performance:** establish Python baselines before setting optimisation targets; record latency and throughput with benchmark results.
- **Type safety:** Pydantic backend contracts and generated TypeScript client types.

## 17. Implementation phases

### Phase 0 — Numerical and instrument specification

- Verify Databento dataset, entitlements, symbology, and available history.
- Confirm SR1/SR3 contract specifications and reference-period formulas.
- Specify meeting-calendar and SOFR-fixing sources.
- Define typed domain schemas and risk-policy structure.
- Select live quote transport and backtest accounting approach.

**Exit condition:** formulas, instrument mapping, schemas, and unresolved assumptions are documented and reviewable.

### Phase 1 — Data and service foundation

- Implement service skeletons, PostgreSQL schema, Parquet raw storage, and configuration.
- Implement historical backfill and live quote ingestion.
- Expose market-health APIs and the initial TypeScript application.

**Exit condition:** real or recorded-live futures data flows reproducibly into normalised storage and the UI.

### Phase 2 — Meeting curve

- Implement RFR accrual, futures pricing, calibration, and diagnostics.
- Build curve and residual screens.

**Exit condition:** the Fed curve can be explained from inputs to prices, including known numerical examples and under-identified cases.

### Phase 3 — House view and trade workflow

- Implement house-view authoring, LLM assistance, approval, trade proposals, and scenario P&L.

**Exit condition:** an approved view produces reproducible market-versus-house trade assessments without automatically entering positions.

### Phase 4 — Risk and paper portfolio

- Implement entry gates, sizing, limits, opportunity costs, exits, and paper ledger.
- Build trade-ticket and portfolio screens.

**Exit condition:** the system demonstrates both a valid entry and explicit rejection due to costs, limits, data health, or opportunity cost.

### Phase 5 — Backtesting and hardening

- Implement point-in-time historical runs using the same trade and risk engine.
- Add reproducibility, performance measurements, failure handling, and operational documentation.

**Exit condition:** live and historical paths produce consistent decisions for the same recorded inputs.

### Phase 6 — Optional extensions

- Profile and introduce C++ where justified.
- Add futures options and Black76 analytics.
- Consider Fed Funds futures and additional central banks as separate expansions.

## 18. Acceptance demonstration

The POC is complete when a reviewer can perform the following from a clean local setup:

1. Start the services and load a defined Fed instrument universe.
2. Backfill a sample and stream or replay live futures quotes.
3. Inspect data health and identify stale/missing inputs.
4. Calibrate a meeting curve and explain every futures residual.
5. Create and approve a house view with visible scenarios and invalidators.
6. Generate an outright and a butterfly proposal.
7. See sizing, binding limits, costs, stress loss, and opportunity cost before entry.
8. Observe one proposal rejected with explicit reasons.
9. Enter an approved paper trade and trigger a documented target, thesis, time, or risk exit.
10. Run a point-in-time backtest using the same rules and inspect net results after costs.
11. Reproduce every step from stored identifiers without hidden cloud dependencies.

## 19. Open decisions before implementation

- Databento live licence upgrade versus an alternative real-time futures feed
- Initial live-schema granularity after the feed is selected: quotes/trades versus MBP1
- Source and import format for Bloomberg generic meeting tickers
- SOFR publication-lag and same-day revision treatment
- Lightweight live event transport between services
- Existing backtest accounting library versus explicit ledger
- Historical sample period and benchmark datasets

These decisions do not change the core architecture. They must be resolved during Phase 0 rather than hidden in implementation assumptions.

## 20. Phase 0 verification log — 2026-11-07

### 20.1 Databento access

Verified using the user's configured API key without exposing it:

- Historical access to `GLBX.MDP3` works.
- The available dataset range reported by the API starts on `2010-06-06` and ends on `2026-11-07`.
- Available schemas include MBO, MBP-1, MBP-10, TBBO, trades, BBO intervals, OHLCV intervals, definition, statistics, and status.
- `SR1.FUT` returned real One-Month SOFR futures daily data.
- `SR3.FUT` returned real Three-Month SOFR futures daily data.
- `SR3.OPT` returned real options-on-SR3 daily data.

Parent subscriptions must use `.FUT` or `.OPT` suffixes. Bare `SR1` and `SR3` with `stype_in='parent'` are rejected by the current API. Parent futures queries also return spreads and structured instruments, so the instrument-normalisation layer must explicitly distinguish outrights from spreads.

**Live-access blocker:** an attempted `bbo-1s` subscription for specific SR1/SR3 outrights failed with:

```text
A live data license is required to access GLBX.MDP3.
```

Therefore historical backfill and recorded-live replay are verified, but genuine Databento real-time ingestion is not. Implementation may build the feed interface and replay workflow, but the acceptance demonstration must not claim live Databento access until a live licence or alternative feed is available.

Sources: [Databento SR3 catalogue](https://databento.com/catalog/cme/GLBX.MDP3/futures/SR3), [Databento SR3 options catalogue](https://databento.com/catalog/cme/GLBX.MDP3/options/SR3), and direct API checks on 2026-11-07.

### 20.2 SR1 contract formula

CME confirms:

- SR1 is cash-settled using the **arithmetic average of daily SOFR values during the contract delivery month**.
- Every calendar day receives a rate; weekends and holidays use the preceding published business-day rate.
- Final settlement is `100 minus R`, with the average rounded to the nearest `0.1bp`.
- Contract value is **$41.67 per basis point per contract**.

The specification's arithmetic-average formula is consistent with CME's methodology when every calendar day receives the same ACT/360 denominator weight.

Sources: [CME SR1 contract specifications](https://www.cmegroup.com/markets/interest-rates/stirs/one-month-sofr/specs), [CME Understanding SOFR Futures](https://www.cmegroup.com/education/articles-and-reports/understanding-sofr-futures), and [CME settlement methodologies](https://www.cmegroup.com/content/dam/cmegroup/education/files/sofr-futures-settlement-calculation-methodologies.pdf).

### 20.3 SR3 contract formula

CME confirms:

- SR3 uses daily SOFR **compounded in arrears** over the contract reference quarter.
- The reference quarter starts on and includes the third Wednesday of the contract-name month and ends on and excludes the third Wednesday three months later.
- Non-business days accrue simple interest using the preceding business-day SOFR; business-day interest compounds.
- The annualised rate uses ACT/360 and is rounded to the nearest `0.01bp` for final settlement.
- Contract value is **$25 per basis point per contract**.
- Contract month names reference the beginning of the reference quarter, not the final settlement month.

The specification's compounded-RFR formula and explicit reference-period modelling are therefore appropriate.

Sources: [CME Understanding SOFR Futures](https://www.cmegroup.com/education/articles-and-reports/understanding-sofr-futures), [CME SR3 rulebook chapter](https://www.cmegroup.com/content/dam/cmegroup/rulebook/CME/V/450/460/460.pdf), and [CME settlement methodologies](https://www.cmegroup.com/content/dam/cmegroup/education/files/sofr-futures-settlement-calculation-methodologies.pdf).

### 20.4 SOFR fixings

The New York Fed's public API was queried successfully:

```text
https://markets.newyorkfed.org/api/rates/secured/sofr/last/5.json
```

It returned official SOFR observations through `2026-11-05`, including effective date, rate, volume, percentiles, and a revision indicator. The latest observation returned during verification was **3.92%** for `2026-11-05`.

The New York Fed publishes at approximately 08:00 ET on business days. Same-day revisions may occur at approximately 14:30 ET, so publication time and revision history must be modelled rather than treating the currently displayed historical value as the value known at 08:00.

Sources: [New York Fed SOFR data](https://www.newyorkfed.org/markets/reference-rates/sofr), [publication and revision information](https://www.newyorkfed.org/markets/reference-rates/additional-information-about-reference-rates), and direct API verification.

### 20.5 Fed meeting calendar

The Federal Reserve's public calendar is verified as a fallback to Bloomberg. It shows the December 8–9, 2026 meeting and the 2027 schedule. Future meetings are tentative until confirmed, so calendars must be versioned rather than treated as immutable.

Bloomberg generic meeting-ticker mappings have not been verified locally and remain a Phase 0 integration item if Bloomberg import is required.

Source: [Federal Reserve FOMC calendars](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm).

### 20.6 Remaining unverified items

- Real-time futures source and entitlement
- Bloomberg meeting-ticker import
- Point-in-time SOFR revision-history retrieval
- Backtest accounting library
- Exact initial historical sample and its storage/cost footprint
