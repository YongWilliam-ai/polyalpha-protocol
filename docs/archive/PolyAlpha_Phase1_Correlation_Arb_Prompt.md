# Claude Code Prompt: Phase 1 — Logical Correlation Arbitrage

> **William**: 請將以下內容貼入 Claude Code 終端機中，讓它實作 Phase 1 的第二個策略：邏輯矛盾套利。

```text
[ROLE & TASK]
You are an expert Web3/AI Tech Lead. Based on the `OpenSource_Integration_Plan.md`, we successfully implemented `yes_no_arb_scanner`. Now, we need to implement the next Phase 1 strategy: **Logical Correlation Arbitrage** (Strategy A3).

[CONTEXT]
- Project: PolyAlpha Protocol
- Target File: `agent/arb_scanner.py`
- Main loop file: `agent/pm_arb_agent.py`

[REQUIREMENTS]
Please execute the following steps ONE BY ONE:

STEP 1: Implement `scan_correlation_arb()`
In `agent/arb_scanner.py`, add a new function `scan_correlation_arb() -> list[dict]`.
- Define a constant map `KNOWN_CORRELATIONS` inside or near the function. Since this is for testing, use a hardcoded example (e.g., Parent: "Will Trump win the 2024 US Presidential Election?" vs Child: "Will a Republican win the 2024 US Presidential Election?"). 
- A logical violation occurs if the Child probability is significantly lower than the Parent probability (e.g., Parent is 60%, but Child is 55%). This is mathematically impossible since Trump IS a Republican.
- For this implementation, fetch active markets via Gamma API (`https://gamma-api.polymarket.com/markets?active=true&limit=100`).
- If you find any market pairs where `price(Specific Outcome) > price(Broader Category) + 0.03` (3% threshold), flag it as an opportunity.
- Return a list of dictionaries with the parent/child market IDs, prices, and the spread.

STEP 2: Integrate into `pm_arb_agent.py`
- Import `scan_correlation_arb` from `arb_scanner`.
- In the main `scan_loop()`, execute this new scanner alongside the existing ones.
- If opportunities are found, log them.

STEP 3: Test and Verify
- Run `python agent/pm_arb_agent.py --once --dry-run` to ensure it executes without crashing.
- Again, it is completely normal if it finds 0 opportunities. We just need the infrastructure to be solid.

When you are done, tell William: "Correlation Arbitrage scanner implemented. Please run: git add -A && git commit -m 'feat: implement correlation_arb_scanner' && git push origin main"
```
