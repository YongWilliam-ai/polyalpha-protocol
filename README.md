# PolyAlpha Protocol

**A DAO-Governed, AI-Driven Market-Making Vault with $PALPHA Tokenized Incentives for Structural Mispricing in Decentralized Prediction Markets**

> ISOM3270 Blockchain Programming in Business Applications — Final Project  
> William Yong | HKUST RMBI Year 2 | Presentation: May 8, 2026

---

## Overview

PolyAlpha is a DeFi protocol on Polygon where users deposit USDC into an ERC-4626 smart contract vault. A rule-based AI agent autonomously detects and exploits the structurally persistent **favorite-longshot pricing bias** on Polymarket. Every trade decision is logged immutably on-chain, and the entire protocol is governed by the **$PALPHA** token.

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
│ DAO.sol      │  test_conn.py    │  PALPHAHub.js (WIP)   │
└──────────────┴──────────────────┴───────────────────────┘
         │               │                    │
         └───────────────┴────────────────────┘
                   Polygon Amoy Testnet
```

## Quick Start

See [SETUP.md](./SETUP.md) for the full step-by-step guide.

```bash
# 1. Install dependencies
npm install

# 2. Configure environment
cp .env.example .env
# Fill in: PRIVATE_KEY, AMOY_RPC_URL, POLYGONSCAN_API_KEY

# 3. Deploy contracts
npm run compile
npm run deploy:amoy

# 4. Run AI agent
cd agent && pip install -r requirements.txt
python agent.py
```

## Project Structure

```
polyalpha-protocol/
├── contracts/
│   ├── PolyAlphaVault.sol      # ERC-4626 vault + logPosition() + circuit breaker
│   ├── PALPHAToken.sol         # 10M max supply ERC-20 with 6-utility stubs
│   └── MockUSDC.sol            # Testnet USDC
├── scripts/
│   └── deploy.js               # Hardhat deploy script (deploys all + smoke test)
├── agent/
│   ├── btc_signal.py           # 7-min BTC momentum signal engine
│   ├── agent.py                # Main scan → signal → log_on_chain loop
│   ├── backtest.py             # Historical strategy backtester
│   ├── test_connection.py      # Verify Polymarket + Binance connections
│   └── requirements.txt        # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.js
│   │   ├── config.js           # Contract addresses + ABIs
│   │   └── pages/
│   │       ├── VaultPage.js    # TVL stats + MetaMask deposit/withdraw
│   │       ├── PositionLogPage.js  # On-chain AI signal audit log
│   │       └── BacktestPage.js # Equity curve chart + win rate
│   └── public/
├── data/                       # Backtest outputs (gitignored)
├── hardhat.config.js
├── package.json
├── .env.example
└── SETUP.md
```

## Key Features

- **ERC-4626 Vault**: Deposit USDC, receive proportional vault shares
- **On-Chain Audit Trail**: Every AI decision logged via `logPosition()` event
- **Rule-Based Signal**: 7-minute BTC momentum + edge threshold (no black box)
- **Quarter-Kelly Sizing**: Mathematically sound position sizing
- **Circuit Breaker**: Auto-halt at 20% drawdown from peak NAV
- **$PALPHA Token**: 6-utility token (governance, staking, fee discounts, burn)
- **DAO Governance**: 48-hour timelock on all parameter changes

## Demo Path (3 minutes)

1. Open dashboard → Vault page → Show vault stats
2. Connect MetaMask (Polygon Amoy) → Deposit 100 test USDC
3. Show deposit tx on Polygonscan
4. Switch to AI Signal Log → Show `logPosition()` events
5. Click Tx ↗ on any signal → Show oracle hash + AI probability
6. Switch to Backtest → Show equity curve and win rate
7. Close: *"Every decision. On-chain. Forever. No black box."*

## Tech Stack

| Layer | Technology |
|---|---|
| Blockchain | Polygon Amoy Testnet (chainId: 80002) |
| Smart Contracts | Solidity ^0.8.20, OpenZeppelin, Hardhat |
| AI Agent | Python 3.11, web3.py, requests |
| Frontend | React 18, ethers.js v6, Recharts, Tailwind CSS |
| Deployment | Vercel (frontend), Polygon Amoy (contracts) |

## License

MIT — Open source after course submission (May 2026).

---

*Built by William Yong for ISOM3270 @ HKUST, April–May 2026*
