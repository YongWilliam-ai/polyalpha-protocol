# PolyAlpha Protocol — Project Memory for Claude Code

> This file is automatically loaded by Claude Code at the start of every session.
> It contains all project constraints, architecture decisions, and collaboration rules.
> DO NOT delete or modify this file without consulting the team.

## Project Overview
PolyAlpha Protocol is a Web3 + AI project combining:
- A Polymarket ERC-4626 vault (PolyAlphaVault.sol)
- A rule-based AI trading agent (agent/agent.py)
- A React + TailwindCSS dashboard (frontend/)
- A $PALPHA token economy (staking, buyback-burn, DAO governance)

**Course**: ISOM3270 Final Project, HKUST
**Student**: William Yong (翁澤宗)
**GitHub**: YongWilliam-ai/polyalpha-protocol (private)

---

## Collaboration Rules (CRITICAL)

Three parties work on this project. You must understand your role:

| Party | Role | What they do |
|---|---|---|
| **Claude Code (you)** | Smart Contract + Python Dev | Write/edit local files, run compile/test |
| **Manus (another AI)** | Tech Lead + QA | Reviews GitHub, fixes bugs, builds frontend |
| **William** | Project Owner | Runs `git push`, makes decisions, runs deploys |

**After completing any task, ALWAYS tell William to run:**
```
git add -A
git commit -m "feat: <short description>"
git push origin main
```
Never push directly yourself. William must push.

---

## Technical Constraints (MUST FOLLOW)

### Solidity
- Version: **exactly `0.8.25`** (no `^` caret)
- EVM: **`cancun`** (set in hardhat.config.js, do not change)
- OpenZeppelin: **v5 only**
- Encoding: **ASCII only** in all `.sol` files — NO Unicode chars (em dash `—`, box drawing `─`, multiply `×`, greater-equal `≥`, etc.)
- Network: Polygon Amoy Testnet (chainId: 80002) or ChainLab Testnet

### Python Agent
- PnL calculation: **cash-flow model only** (runes_leo method) — never use simple odds difference
- Hypothesis Validation: every strategy must have a Hypothesis ID and Kill Criteria
- Kill Criteria: win rate < 52% after 50 trades OR max drawdown > 15%
- Safety: 6-step BitPilot security check chain before every trade execution

### Frontend
- Stack: React + TailwindCSS
- Config: `frontend/src/config.js` contains all contract addresses
- Do NOT hardcode addresses anywhere else

---

## Deployed Contracts (ChainLab Testnet)

| Contract | Address |
|---|---|
| MockUSDC | `0x77D7D52eE789B7C6bcD94eb87e2391BBb94A8D0a` |
| PALPHAToken | `0x36381Cd13C9030Eb7dfa7C274837115370FEcdbF` |
| PolyAlphaVault | `0x1c275054C7159aBBF446E652A744EFB8cbf6efd0` |
| ALPHAStakingPool | `0xF8E9E3af72E1F673B21eCB4d96C99BF9c1D47832` |
| PALPHABuybackBurn | `0xEc33dBc9dFAa1c380863547C5bCB7597eD611Ea4` |
| PolyAlphaDAO | `0x03C56c5bFc857694ECfdfCCa49456d67340E2BF0` |

**IMPORTANT**: Do NOT modify the above addresses. They are live on testnet.

---

## Current Project Status (as of 2026-05-04)

### Completed ✅
- [x] PolyAlphaVault.sol — ERC-4626 vault with Quarter-Kelly sizing
- [x] PALPHAToken.sol — 10M max supply ERC-20
- [x] MockUSDC.sol — testnet USDC
- [x] ALPHAStakingPool.sol — Synthetix-style 10% APY staking
- [x] PALPHABuybackBurn.sol — buyback and burn mechanism
- [x] PolyAlphaDAO.sol — 48h timelock governance (WRITTEN, not deployed)
- [x] agent/btc_signal.py — BTC momentum signal engine with dual-source oracle
- [x] agent/agent.py — V2 compatible, 6-step safety chain
- [x] agent/backtest.py — Hypothesis Validation Framework with cash-flow PnL
- [x] frontend/ — React dashboard with Vault, AI Signal Log, Backtest pages

### Pending ⏳
- [x] Deploy PolyAlphaDAO.sol to testnet (0x03C56c5bFc857694ECfdfCCa49456d67340E2BF0)
- [x] Run backtest and generate backtest_summary.json + equity_curve.csv
- [x] Copy backtest output to frontend/public/
- [x] Add $PALPHA Hub page to frontend (staking, governance, buyback history)
- [ ] Record 3-minute demo video
- [ ] Write final PDF report
- [ ] Execute EdgeBuild UI upgrade (Phase 2 prompt ready in `PolyAlpha_Phase2_EdgeBuild_MiroFish_Prompt.md`)
- [ ] Add MiroFish swarm stub to `agent/pm_arb_agent.py`
- [ ] Deploy frontend to Vercel (guide: `docs/Vercel_Deployment_Guide.md`)

---

## Key Architecture Decisions

1. **Why ChainLab Testnet instead of Amoy?** Amoy faucet was unreliable. ChainLab provided stable test MATIC.
2. **Why no GPT-4o in the agent?** Cost saving. Rule-based momentum + Kelly sizing is sufficient for the demo.
3. **Why ERC-4626?** Prof. Lei specifically asked for vault standard compliance.
4. **Why 48h timelock in DAO?** Matches industry standard (Compound, Aave) and satisfies course requirements.

---

## Common Mistakes to Avoid

1. **NEVER** use Unicode characters in Solidity files (caused 3 compile failures)
2. **NEVER** change the Solidity version or evmVersion
3. **NEVER** modify deployed contract addresses
4. **NEVER** push directly — always tell William to push
5. **NEVER** use `npm run push` alone — use explicit `git add -A && git commit -m "..." && git push origin main`

---

## Key Documents Added (2026-05-04)

| Document | Location | Purpose |
|---|---|---|
| Qlib Evaluation Report | `docs/Qlib_Evaluation_Report_PolyAlpha.md` | Phase 2/3 ML research engine roadmap |
| Vercel Deployment Guide | `docs/Vercel_Deployment_Guide.md` | Frontend hosting for demo |
| Phase 2 EdgeBuild Prompt | `PolyAlpha_Phase2_EdgeBuild_MiroFish_Prompt.md` | UI upgrade + MiroFish stub prompt for Claude Code |
| Complete Revised Project | `PolyAlpha Protocol — Complete Revised Project.md` | Full v2.0 project spec with Prof. Lei feedback responses |
