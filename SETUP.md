# PolyAlpha Protocol — Setup Guide

## Day 1–3: Deploy the Vault

### 1. Install contract dependencies
```bash
npm install
```

### 2. Configure environment
```bash
cp .env.example .env
# Fill in: PRIVATE_KEY, AMOY_RPC_URL, POLYGONSCAN_API_KEY
```

Get test MATIC for Amoy:
- https://faucet.polygon.technology/ (select Amoy)

### 3. Deploy to Polygon Amoy
```bash
npm run compile
npm run deploy:amoy
```

Save the output addresses into `.env`:
```
VAULT_CONTRACT_ADDRESS=0x...
MOCK_USDC_ADDRESS=0x...
```

### 4. Verify on Polygonscan (optional but good for demo)
```bash
npx hardhat verify --network amoy <VAULT_ADDRESS> <USDC_ADDRESS> <AGENT_ADDRESS>
```

---

## Day 4–6: Run the Python Agent

### 5. Set up Python environment
```bash
cd agent
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

### 6. Test connections
```bash
python test_connection.py
```
Expected: prints BTC price + list of active BTC markets

### 7. Test signal generation
```bash
python btc_signal.py
```
Expected: prints a test signal with oracle hash

### 8. Run agent in dry-run mode (no vault needed yet)
```bash
python agent.py
# Auto-detects if vault not deployed → runs as dry run
```

### 9. Run agent in live mode (vault deployed)
```bash
# Ensure VAULT_CONTRACT_ADDRESS is set in .env
python agent.py
# Watch Polygonscan Amoy for PositionLogged events
```

---

## Day 7–9: Run Backtest

### 10. Backtest via Gamma API (no download needed)
```bash
python backtest.py --source gamma --limit 300
```

### 10b. Backtest via Becker CSV (better data)
Download: https://github.com/Jon-Becker/prediction-market-analysis
Place CSV in: `data/polymarket_markets.csv`
```bash
python backtest.py --source csv
```

### 11. Copy results to dashboard
```bash
cp ../data/backtest_summary.json ../frontend/public/
cp ../data/equity_curve.csv ../frontend/public/
```

---

## Day 10–12: Run Dashboard

### 12. Set up React dashboard
```bash
cd ../frontend
npm install
```

Create `frontend/.env`:
```
REACT_APP_VAULT_ADDRESS=0x<your vault address>
REACT_APP_PALPHA_ADDRESS=0x<your palpha address>
```

### 13. Run locally
```bash
npm start
# Opens at http://localhost:3000
```

### 14. Deploy to Vercel (free with GitHub Student Pack)
```bash
npm run build
# Push to GitHub → connect to Vercel → auto-deploys
```

---

## Demo Path (3 minutes for Prof. Lei)

1. Open dashboard → Vault page → Show vault stats
2. Connect MetaMask (Polygon Amoy) → Deposit 100 test USDC
3. Show deposit tx on Polygonscan
4. Switch to AI Signal Log → Show logPosition() events
5. Click Tx ↗ on any signal → Show the full on-chain event with oracle hash
6. Switch to Backtest → Show equity curve and win rate
7. Close: "Every decision. On-chain. Forever. No black box."

---

## Quick Troubleshooting

| Problem | Fix |
|---|---|
| `Cannot connect to RPC` | Check AMOY_RPC_URL in .env. Try: `https://polygon-amoy.blockpi.network/v1/rpc/public` |
| `VAULT_CONTRACT_ADDRESS not set` | Run deploy.js first |
| `Only AI agent` error | Agent wallet address must match `aiAgent` in vault contract |
| No markets in scan | Polymarket may have no active BTC 15m markets right now — check polymarket.com |
| MetaMask wrong network | Switch to Polygon Amoy (chainId: 80002) |
