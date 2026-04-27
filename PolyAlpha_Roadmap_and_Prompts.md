# PolyAlpha Protocol — 完整 Roadmap 與後續 Claude Code Prompts

根據你提供的三份文件（完整執行清單、6大開源整合方案、假設驗證框架）以及目前的 GitHub 狀態，我為你整理了**接下來所有的待辦事項**，並將它們拆分為三個具體的 Claude Code 執行週期（Period 4, 5, 6）。

---

## 🗺️ 剩餘任務全景圖 (Roadmap)

目前我們已經完成了 Period 1-3（合約部署、回測修復、DAO與前端Hub）。接下來的任務分為三個階段：

### 🟢 Period 4: Python Agent 開源整合 (Data & Risk)
- **目標**：升級 `agent.py` 和 `btc_signal.py`，整合 Polymarket V2 數據、新聞情緒過濾器，以及經驗凱利公式。
- **開源資源**：`polymarket-toolkit` (V2), `daily-news` (MCP), `@RohOnChain` (Empirical Kelly), `BitPilot` (6-step safety)。

### 🟡 Period 5: 假設驗證框架與 PnL 重構 (Strategy Evaluation)
- **目標**：徹底重構 `backtest.py`，實作 runes_leo 的「假設驗證框架」與「現金流 PnL 模型」。
- **開源資源**：`runes_leo` (Hypothesis Validation & Cash-flow PnL)。

### 🔴 Period 6: X (Twitter) 社交整合與 Dashboard 完善
- **目標**：在前端加入 X (Twitter) 資訊流，讓 Dashboard 顯示即時的 Polymarket 相關推文，並完成最終的 UI 潤飾。
- **開源資源**：`polyainews`, `brief.day1`, `conway` 等 X 資訊流工具。

---

## 📝 執行指南與 Prompts

請**依序**開新的 Claude Code 對話，並貼上對應的 Prompt。

### 🚀 Period 4 Prompt: Python Agent 開源整合 (Data & Risk)

> **操作指示**：在 VS Code 終端機輸入 `claude` 啟動新的對話，然後貼上以下內容。

```text
[CONTEXT & MEMORY - Read this carefully before starting]

Project: PolyAlpha Protocol (ISOM3270 Final Project)
Working Directory: C:\Users\user\Desktop\Dev.items.folder\ISOM3270_Startup
GitHub: YongWilliam-ai/polyalpha-protocol (private)

== What has been completed ==
1. All 6 contracts deployed to ChainLab Testnet.
2. Frontend React dashboard: 4 pages (Vault, AI Signal Log, Backtest, PALPHA Hub).
3. Python Agent currently uses basic momentum rules + theoretical Kelly sizing.

== Current Task Goal ==
Upgrade the Python Agent (`agent.py`, `btc_signal.py`) by integrating open-source resources to improve data quality and risk management.

[TASK 1: Data Fetching Layer — Update btc_signal.py & agent.py]
1a. Add a function `get_polymarket_v2_odds(market_id)` in `btc_signal.py`:
    - Primary: use `runesleo/polymarket-toolkit` logic (V2 compatible).
    - Fallback: use Gamma API (`https://gamma-api.polymarket.com/markets/{id}`).
    - If `polymarket-toolkit` is not installed, write as a stub with TODO comment.

1b. Add a function `get_news_sentiment()` in `agent.py`:
    - Call: `https://ai.6551.io/open/free_hot?category=crypto` (no API key needed).
    - Parse the response and return "bullish", "bearish", or "neutral".
    - Use this as a pre-filter: skip trade if sentiment is "bearish" and signal is UP.
    - Comment: "# Inspired by 6551Team/daily-news MCP Server".

[TASK 2: Risk Management Layer — Update btc_signal.py & agent.py]
2a. Upgrade `monte_carlo_kelly()` to `empirical_kelly()` in `btc_signal.py`:
    - Instead of using a fixed theoretical win_rate, use the ACTUAL win rate from the last N trades stored in a rolling window (default N=50).
    - If fewer than 10 trades in history, fall back to `monte_carlo_kelly()`.
    - Add a parameter `trade_history: list[dict]` (list of past {"won": bool} records).
    - Comment: "# Inspired by @RohOnChain Empirical Kelly research".

2b. Implement the 6-step safety chain in `agent.py`'s main loop:
    - Ensure `safety_check_chain()` is called before ANY execution.
    - Comment: "# Inspired by duolaAmengweb3/bgtask (BitPilot)".

[CONSTRAINTS]
- Do NOT modify any Solidity contracts (`.sol` files) or deployment scripts.
- Do NOT modify `backtest.py` in this step.
- Ensure all new Python code has comments explaining which open-source resource inspired it.

[WORKFLOW]
1. Complete the tasks.
2. Tell William: "Period 4 Agent upgrade complete. Please run:
git add -A
git commit -m 'feat: Python Agent V2 upgrade - polymarket-toolkit + empirical kelly + news sentiment'
git push origin main"
```

---

### 🚀 Period 5 Prompt: 假設驗證框架與 PnL 重構

> **操作指示**：等 Period 4 完成並 push 後，在 Claude Code 輸入 `/compact`，然後貼上以下內容。

```text
[CONTEXT & MEMORY - Read this carefully before starting]

Project: PolyAlpha Protocol (ISOM3270 Final Project)
Working Directory: C:\Users\user\Desktop\Dev.items.folder\ISOM3270_Startup
GitHub: YongWilliam-ai/polyalpha-protocol (private)

== What has been completed ==
1. Python Agent upgraded with V2 data fetching, news sentiment, and empirical Kelly.
2. Backtest engine currently has basic Kill Criteria but needs a full structural upgrade based on runes_leo's research.

== Current Task Goal ==
Upgrade `agent/backtest.py` to implement a strict "Hypothesis Validation Framework" and a Cash-Flow based PnL model.

[TASK 1: Hypothesis Tracking & Kill Criteria]
Update `backtest.py`:
- The backtester must accept a "Hypothesis ID" (e.g., "H1_BTC_Momentum") and log all results under this ID.
- Implement strict stop-loss and kill conditions during the backtest loop:
  * If win rate drops below 52% after 50 trades -> KILL.
  * If Max Drawdown exceeds 15% -> KILL.
  * If Slippage (simulated) exceeds 2% -> PAUSE.

[TASK 2: Cash-Flow Based PnL]
Update the PnL calculation in `backtest.py`:
- Do NOT rely on simple `(Odds_Close - Odds_Open)` calculations.
- Implement a cash-flow model:
  * Starting Balance: $1000
  * Deduct cost when buying shares (`Cost = Shares * Odds`).
  * Add payout when market resolves (`Payout = Shares * 1` if won, else 0).
  * Calculate PnL based on the actual change in Balance.
- Comment: "# Inspired by runes_leo Cash-Flow PnL research".

[TASK 3: Autopsy Report Generation]
- If a strategy hits a Kill Criterion, the backtester must output a detailed "Autopsy Report" (e.g., saved to `agent/logs/H1_autopsy.txt`) detailing exactly which condition was breached and at what trade number.

[CONSTRAINTS]
- Do NOT modify any Solidity contracts or `agent.py`/`btc_signal.py`.
- Ensure the Python code is clean, modular, and well-commented.

[WORKFLOW]
1. Update `agent/backtest.py`.
2. Run: `python agent/backtest.py --source dummy` to ensure the Kill Criteria and Autopsy Report generation work correctly.
3. Tell William: "Period 5 Backtest engine upgraded. Please run:
git add -A
git commit -m 'feat: implement Hypothesis Validation Framework and Cash-Flow PnL'
git push origin main"
```

---

### 🚀 Period 6 Prompt: X (Twitter) 社交整合與 Dashboard 完善

> **操作指示**：等 Period 5 完成並 push 後，在 Claude Code 輸入 `/compact`，然後貼上以下內容。

```text
[CONTEXT & MEMORY - Read this carefully before starting]

Project: PolyAlpha Protocol (ISOM3270 Final Project)
Working Directory: C:\Users\user\Desktop\Dev.items.folder\ISOM3270_Startup
GitHub: YongWilliam-ai/polyalpha-protocol (private)

== What has been completed ==
1. Smart contracts, Python Agent, and Backtest engine are fully upgraded and integrated with open-source logic.
2. Frontend has 4 pages (Vault, PositionLog, Backtest, PALPHAHub).

== Current Task Goal ==
Integrate X (Twitter) social feeds into the frontend dashboard to provide real-time market context, inspired by open-source tools like `polyainews` and `brief.day1`.

[TASK 1: Create SocialFeed Component]
Create a new component `frontend/src/components/SocialFeed.js`:
- This component should display a list of mock/simulated tweets related to Polymarket and Crypto (since we don't have a live Twitter API key).
- Include mock tweets from accounts like `@polymarket_news`, `@polybroapp`, and `@runes_leo`.
- Design it to look like a clean, dark-mode Twitter feed widget.

[TASK 2: Integrate into Dashboard]
Update `frontend/src/pages/VaultPage.js` (or create a new `SocialPage.js` if you prefer):
- Add the `SocialFeed` component to the right side or bottom of the page.
- Add a title: "Live Market Alpha (Inspired by polyainews)".

[TASK 3: Final UI Polish]
- Ensure all 4 tabs in `App.js` navigate smoothly.
- Check that all tables and charts render correctly in dark mode.
- Ensure the "Connect Wallet" button (even if mock) looks professional.

[CONSTRAINTS]
- Do NOT modify any Python or Solidity files.
- Use standard React and CSS (no need to install heavy new libraries unless necessary).

[WORKFLOW]
1. Complete the frontend updates.
2. Run `cd frontend && npm run build` to ensure it compiles.
3. Tell William: "Period 6 Social integration complete. Please run:
git add -A
git commit -m 'feat: integrate X social feed and polish dashboard UI'
git push origin main"
```
