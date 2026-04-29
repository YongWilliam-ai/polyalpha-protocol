# PolyAlpha Protocol

**A DAO-Governed, AI-Driven Market-Making Vault with $PALPHA Tokenized Incentives for Structural Mispricing in Decentralized Prediction Markets**

> ISOM3270 Blockchain Programming in Business Applications — Final Project  
> William Yong | HKUST RMBI Year 2 | Presentation: May 8, 2026

---

## Overview

PolyAlpha is a DeFi protocol where users deposit USDC into an ERC-4626 smart contract vault. A rule-based AI agent autonomously detects and exploits the structurally persistent **favorite-longshot pricing bias** on Polymarket. Every trade decision is logged immutably on-chain, and the entire protocol is governed by the **$PALPHA** token.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    PolyAlpha Protocol                   │
├──────────────┬──────────────────┬───────────────────────┤
│   Contracts  │    AI Agent      │      Frontend         │
│              │                  │                       │
│ Vault.sol    │  btc_signal.py   │  VaultPage.js         │
│ PALPHA.sol   │  agent.py        │  PositionLogPage.js   │
│ Staking.sol  │  backtest.py     │  BacktestPage.js      │
│ DAO.sol      │  test_conn.py    │  PALPHAHub.js         │
└──────────────┴──────────────────┴───────────────────────┘
         │               │                    │
         └───────────────┴────────────────────┘
                   ChainLab Testnet
```

## Current Project Status

- **Contracts**: 6 Core Contracts Deployed to **ChainLab Testnet** (chainId: 31337).
- **Agent**: Python Agent running in Paper Trading Mode (capturing data, logging on-chain, no real money).
- **Frontend**: React Dashboard completed (Vault, AI Signal Log, Backtest, PALPHA Hub).
- **Next Phase**: Integrating open-source Polymarket Alpha strategies and executing dry-run tests.

## Quick Start

```bash
# 1. Install dependencies
npm install

# 2. Configure environment
cp .env.example .env
# Fill in: PRIVATE_KEY, CHAINLAB_RPC_URL

# 3. Deploy contracts
npm run compile
npm run deploy:chainlab

# 4. Run AI agent
cd agent && pip install -r requirements.txt
python agent.py
```

## Key Features

- **ERC-4626 Vault**: Deposit USDC, receive proportional vault shares
- **On-Chain Audit Trail**: Every AI decision logged via `logPosition()` event
- **Rule-Based Signal**: 7-minute BTC momentum + edge threshold (no black box)
- **Quarter-Kelly Sizing**: Mathematically sound position sizing
- **Circuit Breaker**: Auto-halt at 20% drawdown from peak NAV
- **$PALPHA Token**: 6-utility token (governance, staking, fee discounts, burn)
- **DAO Governance**: 48-hour timelock on all parameter changes

## Tech Stack

| Layer | Technology |
|---|---|
| Blockchain | ChainLab Testnet (chainId: 31337) |
| Smart Contracts | Solidity 0.8.25 (cancun), OpenZeppelin v5, Hardhat |
| AI Agent | Python 3.11, web3.py, requests |
| Frontend | React 18, ethers.js v6, Recharts, Tailwind CSS |
| Deployment | Vercel (frontend), ChainLab (contracts) |

## License

MIT — Open source after course submission (May 2026).
