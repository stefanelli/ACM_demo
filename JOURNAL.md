# Aloe Implementation Journal

Session-to-session handoff for decisions, verified findings, blockers, and the current delivery gate. Keep this file concise. See [WIKI.md](WIKI.md) for the technical overview and [SPEC.md](SPEC.md) for detailed requirements.

## Current state — 2026-11-07

- Repository cloned from `git@github.com:stefanelli/ACM_demo.git` into `/home/salvatore/Projects/Aloe/ACM_demo`.
- Original Dash application was installed in `.venv`, launched, and visually checked. The baseline server is stopped.
- The original app starts with a blank default tab; curve marking works after selecting its tab. Databricks execution depends on personal cloud configuration.
- No implementation refactor has started. `SPEC.md`, `WIKI.md`, and `JOURNAL.md` are the only new source files.
- Temporary long-curve FRED data was removed because the project is now meeting-date driven.

## Agreed product direction

Aloe will be a Fed meeting-curve research and paper-trading platform:

```text
Futures data → meeting curve → economist house view → relative-value proposal
             → entry/sizing/limits/exits/opportunity cost → backtest
```

Key decisions:

- Fed only initially; SR1 and SR3 futures are the first instrument universe.
- No generic long-maturity curve demo.
- FastAPI backend services and React + TypeScript + Vite frontend; Dash is excluded.
- PostgreSQL system of record and Parquet immutable raw storage.
- Small microservices: market data, pricing, research/risk, and a backtest worker.
- Risk is central: entry gates, scenario sizing, limits, exits, and opportunity cost are mandatory before paper entry.
- The same pricing, trade, cost, and risk logic is used live and in backtests.
- LLM only assists the economist with structured house views; it cannot approve views or trades.
- Paper execution only; no broker routing.
- C++ is introduced only after Python profiling demonstrates a meaningful benefit.
- Options and Black76 are a later extension, not part of the first complete workflow.
- Pydantic v2 for API models/serialization (FastAPI-native, OpenAPI auto-generation). `msgspec` is a later optimisation candidate for hot JSON paths only if profiling justifies it.

## Verified findings — 2026-11-07

### Databento

- The configured API key works for historical `GLBX.MDP3` data; the secret was not exposed.
- Historical queries returned real data for `SR1.FUT`, `SR3.FUT`, and `SR3.OPT`.
- Dataset range returned: `2010-06-06` through `2026-11-07`.
- Parent symbols require `.FUT` or `.OPT`; bare `SR1`/`SR3` fail.
- Parent futures queries include spreads and structured instruments; outright filtering is required.
- **Live access is blocked:** a real `bbo-1s` subscription failed with `A live data license is required to access GLBX.MDP3.`
- Historical backfill and recorded-live replay are viable. Genuine real-time ingestion needs a live licence or another feed.

### Futures formulas

CME documentation confirms:

- **SR1:** arithmetic average of daily SOFR over the delivery month; weekends/holidays use the preceding published rate; $41.67/bp.
- **SR3:** daily SOFR compounded in arrears over the IMM reference quarter using ACT/360; $25/bp.
- SR3 reference quarter begins on the third Wednesday of the contract-name month and ends three months later; contract names do not identify the final settlement month.
- Curve calibration must expose under-identification, residuals, regularisation, and sensitivity rather than imply a unique meeting path when futures constraints are insufficient.

### Listed liquidity

Direct Databento volume checks for outright contracts on `2026-11-06` returned:

- **SR3:** 2,820,087 contracts
- **ZQ (30-Day Fed Funds):** 423,770 contracts
- **SR1:** 213,950 contracts

Use SR3 as the primary liquidity and price-discovery instrument. ZQ remains useful for direct EFFR/monthly meeting information but is a separate benchmark and is less liquid. SR1 provides monthly SOFR coverage but was least traded of the three in this check. Aggregate volume does not replace contract-level bid/ask and depth checks.

### Reference data

- New York Fed SOFR API works: `https://markets.newyorkfed.org/api/rates/secured/sofr/last/5.json`.
- Verification returned official observations through `2026-11-05`; latest returned SOFR was **3.92%** for that effective date.
- SOFR publication and possible same-day revisions require distinct timestamps and revision-aware storage.
- Official FOMC calendars are available and are a verified fallback to Bloomberg. Future meetings are tentative and calendars must be versioned.

## Current blocker

Choose the real-time futures source:

1. Upgrade Databento live access, or
2. Use an alternative real-time feed, or
3. Continue initial development with historical backfill and recorded-live replay while the feed decision remains open.

Do not describe the application as real-time verified until a real subscription succeeds.

## Roadmap and gates

1. **Phase 0 — close specifications:** verify remaining instrument metadata, Bloomberg ticker import if needed, SOFR revision history, schemas, event transport, backtest accounting, and sample period.
2. **Phase 1 — data foundation:** service skeletons, PostgreSQL/Parquet, TypeScript shell, backfill, live/replay ingestion, and market-health UI. Gate: real SR1/SR3 data reaches storage and UI reproducibly.
3. **Phase 2 — meeting curve:** Python RFR/futures pricing, calibration, residuals, identification, and sensitivity. Gate: every displayed price and meeting assumption is explainable.
4. **Phase 3 — house view and trades:** LLM-assisted scenario editor, approval/versioning, market-versus-house comparison, outrights/spreads/butterflies, and scenario P&L. Gate: reproducible proposals without automatic entry.
5. **Phase 4 — risk and paper portfolio:** entry gates, sizing, limits, opportunity costs, exits, and ledger. Gate: one accepted trade, one explicit rejection, and one documented exit.
6. **Phase 5 — backtesting:** point-in-time data, next-quote execution, rolls, multi-leg costs, identical risk logic, and reproducible results. Gate: replay and backtest decisions agree for identical inputs.
7. **Phase 6 — interview hardening:** clean setup, bundled demo data, failure handling, performance measurements, and the full acceptance demonstration in `SPEC.md`.
8. **Later:** measured C++ optimisation, options/Black76, Fed Funds with an EFFR/SOFR basis model, additional central banks, and ClickHouse only if scale justifies it.

## Immediate next actions

- Select the real-time feed strategy.
- Resolve the remaining Phase 0 choices listed in `SPEC.md` §19.
- Begin Phase 1 only after the user asks to start implementation.

## Remaining unverified items

- Bloomberg generic meeting-ticker import
- Point-in-time SOFR revision-history retrieval
- Backtest accounting library versus explicit ledger
- Final historical sample and storage/cost footprint
- C++ performance justification

Full verification details and sources: [SPEC.md §20](SPEC.md#20-phase-0-verification-log--2026-11-07).
