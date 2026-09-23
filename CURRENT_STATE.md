# PolyAlpha Protocol — Current State

> **As of 2026-09-22.** This is the current-state entry point. Older course reports, pitch scripts and project-state documents are preserved as historical artifacts and may contain superseded numbers or wording.

## What PolyAlpha is today

PolyAlpha is an **academic / research prototype** for auditable prediction-market workflows. It combines an off-chain Python research layer, Solidity testnet contracts and a React dashboard. It is **not a production trading system**.

## Execution status

- The primary BTC path is **paper trading / signal logging**.
- `agent/agent.py` does **not** submit live Polymarket CLOB orders.
- `PolyAlphaVault.logPosition()` emits an audit event; it does **not** execute a Polymarket trade.
- Scanner modules may read live public data, but execution remains paper / informational unless explicitly implemented and reviewed.

## Signal architecture

The primary BTC path is deterministic:

`market scan -> BTC momentum -> ROC/RSI/MACD confirmation -> probability heuristic -> divergence check -> Kelly sizing -> safety checks -> optional on-chain log`

The field name `ai_probability` is historical naming. In this path it is a **signal probability estimate**, not the output of a trained ML model.

`agent/mirofish_integration.py` is a separate experimental LLM research layer. Persona diversity does not imply statistically independent models.

## Backtest / simulation status

`agent/backtest_reproducible.py` is best interpreted as a **reproducible simulation / sensitivity harness**, not evidence of historical live alpha.

It uses real closed-market metadata, reconstructed / approximate entry prices and an assumed signal-accuracy process. Resulting win rate, Sharpe, drawdown and P&L are outputs of those assumptions.

## Current contract parameters

- Solidity `0.8.25`
- ERC-4626 vault
- Performance fee `20%`
- Management fee `0.5%` annual
- Vault max-position constant `5% TVL`
- Vault drawdown halt `20%`
- PALPHA max supply `10,000,000`
- PALPHA initial mint `3,000,000`
- Staking prototype `10% APY`
- DAO proposal threshold `1,000 PALPHA`
- DAO quorum `100,000 PALPHA`
- DAO voting period `48 hours`

## Current limitations

- no production CLOB execution in the primary agent;
- demo / cached frontend fallbacks exist and should be labelled;
- social feed is simulated;
- DAO voting uses current balances rather than snapshots;
- vault drawdown is not flow-adjusted;
- `MAX_EXPOSURE_BPS` lacks a full on-chain exposure ledger;
- oracle input hashes are tamper evidence, not source attestation;
- risk logic is duplicated across experimental pipelines;
- contracts are not professionally audited.

## Document precedence

When documents disagree, use:

1. executable source code;
2. `CURRENT_STATE.md`;
3. `README.md`;
4. dated audits / technical-debt files;
5. historical course reports and pitch scripts.
