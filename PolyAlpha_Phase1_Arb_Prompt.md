# Claude Code Prompt: Phase 1 — Riskless Arbitrage Implementation

> **William**: 請將以下內容貼入 Claude Code 終端機中，讓它開始實作 Phase 1 最高優先級的無風險套利策略。

```text
[ROLE & TASK]
You are an expert Web3/AI Tech Lead. Based on the `OpenSource_Integration_Plan.md` you just generated, the highest-ROI next task for PolyAlpha Protocol is implementing the `yes_no_arb_scanner()` (Strategy 4).

[CONTEXT]
- Project: PolyAlpha Protocol
- Goal: Implement mathematical riskless arbitrage (YES + NO < $1.00)
- Target File: `agent/arb_scanner.py`
- Main loop file: `agent/pm_arb_agent.py`

[REQUIREMENTS]
Please execute the following steps:

STEP 1: Implement `scan_yes_no_arb()`
In `agent/arb_scanner.py`, add a new function `scan_yes_no_arb(market_ids: list[str]) -> list[dict]`.
- For each market_id, fetch the best ASK price for the YES token and the best ASK price for the NO token.
- Use the CLOB REST API `https://clob.polymarket.com/book?token_id={id}` to get the best ask.
- A market is profitable if `(best_yes_ask + best_no_ask) < 0.98` (leaving a 2% buffer for fees/gas).
- Return a list of opportunities containing `market_id`, `yes_price`, `no_price`, and `profit_pct`.

STEP 2: Integrate into `pm_arb_agent.py`
- Import `scan_yes_no_arb` from `arb_scanner`.
- In the main `scan_loop()`, execute this new scanner alongside the existing ones.
- If opportunities are found, log them and send them via the existing Telegram alert system.

STEP 3: Test and Verify
- Run `python agent/pm_arb_agent.py --once --dry-run` to ensure it executes without crashing.
- Do not worry if no real opportunities are found right now (it's rare), just ensure the logic and API calls work.

When you are done, tell William: "Riskless YES/NO arbitrage scanner implemented. Please run: git add -A && git commit -m 'feat: implement yes_no_arb_scanner' && git push origin main"
```
