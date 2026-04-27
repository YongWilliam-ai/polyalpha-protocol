# PolyAlpha Protocol — 盈利策略評估與執行 Prompt (For Claude Opus & Claude Code)

William，我完全理解你的需求。作為一個 Startup，**「能賺錢」才是唯一的硬道理**。

你提供的資源非常強大：
1. **`funding-rates-mcp`**：能一次掃描 9 家交易所（HL, Binance, Bybit, OKX 等），計算扣除手續費後的「真實淨值」，這是無風險套利（Arbitrage）的聖杯。
2. **Hyperliquid MCP**：帶有判斷層的合約數據，能直接問 AI「現在哪裡有爆倉風險」、「鯨魚在做多還是做空」。
3. **Polymarket 快結算套利**：尋找 95%+ 確定性、即將結算的盤口，利用時間差套利。

為了實現這個目標，我為你準備了**兩份 Prompt**：
- **Prompt A**：給 Claude Opus（網頁版）的，讓它幫你評估這個商業模式和策略邏輯。
- **Prompt B**：給 Claude Code（終端機）的，讓它直接把這些 MCP 工具整合進我們的 `agent.py` 中。

---

## 📝 Prompt A: 給 Claude Opus (網頁版) 的策略評估 Prompt

> **操作指示**：複製以下全部內容，貼到 Claude Opus (Web) 中。

```text
[Role & Context]
You are an elite Quantitative Researcher and Web3 Startup Advisor. I am William, a Year 2 RMBI student at HKUST, building "PolyAlpha Protocol" — an AI-driven trading agent and vault system. 
My goal is to turn this university project into a real, profitable startup. I need your expert evaluation on my proposed trading strategies.

[Current Infrastructure]
- Smart Contracts: Vault, Token, Staking, DAO (Deployed on Testnet).
- Backtest Engine: Implements runes_leo's Hypothesis Validation Framework and Cash-flow PnL model.
- AI Agent: Currently uses basic momentum + empirical Kelly sizing.

[Proposed Profit Strategies]
I want to pivot the AI Agent to focus on two highly deterministic, low-risk arbitrage strategies:

Strategy 1: Polymarket Fast-Resolution Arbitrage (95%+ Certainty)
- Logic: Scan Polymarket for markets that are extremely close to resolution (e.g., < 2 hours left) where the "YES" or "NO" share price is already at $0.95 or $0.96.
- Action: The AI agent buys these shares to capture the remaining 4-5% spread, assuming the event outcome is already practically guaranteed (e.g., a sports game in the final minutes with a huge score gap, or a political event that just concluded but hasn't resolved on-chain yet).

Strategy 2: Cross-Exchange Funding Rate Arbitrage (Delta-Neutral)
- Tools: I will integrate `funding-rates-mcp` (by @hunterweb303) which scans 9 exchanges (Hyperliquid, Binance, Bybit, OKX, dYdX, etc.) to calculate the *net* spread after taker fees.
- Logic: Find extreme funding rate differences between exchanges (e.g., BTC funding is 10.95%/yr on HL, but 6.34%/yr on Paradex).
- Action: The agent executes a delta-neutral position (Long on the low-funding exchange, Short on the high-funding exchange) to harvest the funding fee spread.

[Your Task]
Please evaluate these two strategies based on the following criteria:
1. Feasibility & Risks: What are the hidden risks? (e.g., slippage, execution latency, liquidity constraints, API rate limits).
2. Capital Efficiency: For a startup with limited initial capital ($500 - $1000), which strategy offers a better risk-adjusted return?
3. Technical Implementation: What specific challenges will my Python agent face when executing these? (e.g., gas fees on Polygon vs. Hyperliquid L1).
4. Conclusion: Give me a harsh, realistic verdict. Can this actually make money? If yes, what is the exact next step I should take to test it?
```

---

## 💻 Prompt B: 給 Claude Code (終端機) 的執行 Prompt

> **操作指示**：在 Claude Opus 評估完畢，且你決定要整合這些工具後，在 VS Code 終端機輸入 `claude`，然後輸入 `/compact`，接著貼上以下 Prompt。

```text
[CONTEXT & MEMORY - Read this carefully before starting]

Project: PolyAlpha Protocol (ISOM3270 Final Project)
Working Directory: C:\Users\user\Desktop\Dev.items.folder\ISOM3270_Startup
GitHub: YongWilliam-ai/polyalpha-protocol (private)

== What has been completed ==
1. Core infrastructure (Contracts, Frontend, Backtest Engine) is 100% complete.
2. The project is now pivoting from a "university demo" to a "profitable startup".
3. We are abandoning the simple BTC momentum strategy and moving towards Delta-Neutral Funding Arbitrage and Polymarket Fast-Resolution Arbitrage.

== Current Task Goal ==
Integrate the open-source `funding-rates-mcp` and `bitget-task-skills` into our AI Agent ecosystem to enable real-time arbitrage scanning.

[TASK 1: Install MCP Servers]
We need to configure the Claude Code environment to use the new MCP servers.
Update (or create) the `.claude/mcp.json` file in the project root to include:
1. `funding-arb-scanner`:
   Command: `npx`, Args: `["-y", "@cexagent/funding-arb-scanner"]`
2. `hyperliquid-mcp`:
   Command: `npx`, Args: `["-y", "@cexagent/hyperliquid-mcp"]`

[TASK 2: Create Arbitrage Scanner Script]
Create a new file `agent/arb_scanner.py`. This script will NOT execute trades yet (we are in Paper Trading phase), but it will scan for opportunities.
Implement two functions:
1. `scan_funding_arbitrage()`:
   - Write a stub/wrapper that conceptually calls the MCP tool `scan_funding_diff()` to find the highest net-spread funding pairs across Binance, HL, and OKX.
   - Log the top 3 opportunities to the console.
2. `scan_polymarket_fast_resolution()`:
   - Write a script that fetches active Polymarket markets.
   - Filter for markets where `price > 0.95` AND `volume > 10000`.
   - Log these "high-certainty" markets to the console.

[TASK 3: Update agent.py Main Loop]
Modify `agent/agent.py`:
- Import the two new functions from `arb_scanner.py`.
- In the main `run_agent()` loop, instead of just checking BTC momentum, it should now run `scan_funding_arbitrage()` and `scan_polymarket_fast_resolution()`.
- If an opportunity is found, log it to `agent/logs/arbitrage_opportunities.txt`.

[CONSTRAINTS]
- Do NOT modify any Solidity contracts or the React frontend.
- This is a read-only / scanning update. Do NOT implement private key signing or actual trade execution yet.
- Ensure all code is well-commented, referencing "@hunterweb303 funding-rates-mcp".

[WORKFLOW]
1. Complete the MCP configuration and Python script creation.
2. Run `python agent/arb_scanner.py` to test the logic (it's okay if it just prints mock data or stubs for now, as long as the structure is correct).
3. Tell William: "Arbitrage Scanner integrated. Please run:
git add -A
git commit -m 'feat: integrate funding-rates-mcp and Polymarket fast-resolution scanner'
git pull origin main --rebase
git push origin main"
```
