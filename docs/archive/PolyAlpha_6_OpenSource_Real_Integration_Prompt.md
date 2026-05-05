# PolyAlpha Protocol — 6 大開源資源「真實整合」 Claude Code Prompt

**執行方式：**
請將以下內容**全部複製**，直接貼進 VS Code 終端機的 Claude Code 中執行。

---

```text
[ROLE & CONTEXT]
You are an expert Quantitative Developer and Web3 Architect. 
William has audited the previous integrations and found that many were just "mocks" or "stubs" (e.g., SocialFeed is hardcoded, polymarket-toolkit is just a comment, bgtask safety check is simulated).
Your mission now is to perform a REAL, code-level integration of the core logic from these open-source repositories into the PolyAlpha Python Agent.

[GOAL: REAL Open-Source Core Logic Porting]
Instead of npm installing the entire repos (which are standalone apps/servers), you will PORT their core logic files directly into our `agent/` directory to make them natively run within our Python environment.

Please execute the following tasks sequentially. Make sure to actually write the functional Python code based on the provided logic rules. Do NOT use mocks.

---

### TASK 1: Real Polymarket V2 SDK Integration (`runesleo/polymarket-toolkit`)
**Background:** The original toolkit is in TypeScript (`src/index.ts`), but we need its exact API endpoints in Python.
**Action in `agent/btc_signal.py`:**
- Replace the `get_polymarket_v2_odds` stub with real HTTP calls.
- **Primary:** Call `https://clob.polymarket.com/midpoint?token_id={market_id}` to get the live orderbook midpoint.
- **Fallback:** Call `https://gamma-api.polymarket.com/markets/{market_id}` to get `outcomePrices[0]`.
- Remove the `TODO: once installed, replace stub` comment. Make it actually return the parsed float.

### TASK 2: Real News Sentiment API (`6551Team/daily-news`)
**Background:** The original is an MCP server calling a REST API. We will call the REST API directly.
**Action in `agent/btc_signal.py`:**
- Update `get_macro_sentiment()`.
- Make a real HTTP GET request to `https://ai.6551.io/open/free_hot?category=crypto&limit=10`.
- Parse the JSON response. Count how many items have `"signal": "bullish"` vs `"bearish"`.
- Rule: if bullish > bearish + 2 return "BULLISH"; if bearish > bullish + 2 return "BEARISH"; else "NEUTRAL".
- Handle `requests.exceptions.RequestException` gracefully (return "NEUTRAL" on fail).

### TASK 3: Real Safety Gate Logic (`duolaAmengweb3/bgtask`)
**Background:** The original `safety-gate.ts` implements a strict 6-step check. We need this exact logic in Python.
**Action in `agent/execution_engine.py` (or create `agent/safety_gate.py`):**
- Implement `run_safety_checks(amount_usdt, total_assets, symbol, side)`.
- Rule 1 (Daily Limit): Check a local file `daily_trades.json`. If today's trades >= 5, return `False`.
- Rule 2 (Position Limit): If `amount_usdt / total_assets > 0.1` (10% max), return `False`.
- Rule 3 (Confirm Threshold): If `amount_usdt > 1000`, return `False` (daemon mode auto-rejects large orders).
- If all pass, return `True`. 
- Update `pm_arb_agent.py` to call this BEFORE any trade execution.

### TASK 4: Real Momentum Scorer & Empirical Kelly (`bgtask` + `@RohOnChain`)
**Background:** `momentum-scorer.ts` uses ROC(40%) + RSI(30%) + MACD(30%).
**Action in `agent/btc_signal.py`:**
- We already have `btc_momentum`. Now, implement a real `empirical_kelly(win_rate, odds)` function.
- Read `agent/trade_history.jsonl` to calculate the *actual* historical win rate of our agent over the last 30 trades.
- If we have < 10 trades, use the theoretical `win_rate`.
- Calculate Kelly: `f* = (p * b - q) / b` where `p` = empirical win rate, `b` = `(1 / odds) - 1`.
- Clamp the result between 0.01 and 0.1 (1% to 10% max).

### TASK 5: Real Cash-Flow PnL (`runesleo/polymarket-toolkit`)
**Background:** The `compute_precise_pnl.py` script calculates PnL as `SUM(SELL) + SUM(REDEEM) - SUM(BUY)`.
**Action in `agent/backtest.py`:**
- Rewrite the `calculate_pnl()` function.
- Do NOT rely on a simple `profit = (exit - entry)`.
- Parse the simulated trade history to sum up total USDC spent on BUYs, and total USDC received from SELLs/REDEEMs.
- `Realized PnL = Total Received - Total Spent`.

---

[EXECUTION INSTRUCTIONS]
1. Read the instructions carefully. Do not just add comments saying "Inspired by...". Write the actual Python logic.
2. For HTTP requests, use the `requests` library.
3. For file I/O (like `daily_trades.json` or `trade_history.jsonl`), use the `json` and `os` modules.
4. When you finish modifying all files, run a quick syntax check: `python3 -m py_compile agent/*.py`
5. Finally, commit the changes: `git add -A && git commit -m "feat: real port of open-source logic (Polymarket V2, 6551 API, bgtask safety, cash-flow PnL)"`
```
