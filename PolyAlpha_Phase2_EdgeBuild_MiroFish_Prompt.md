# PolyAlpha Protocol — Phase 2: EdgeBuild UI & MiroFish 真實核心移植

**執行方式：**
請將以下內容**全部複製**，直接貼進 VS Code 終端機的 Claude Code 中執行。

---

```text
[ROLE & CONTEXT]
You are an expert Web3 Frontend Developer and AI Architect. We are entering Phase 2 of the PolyAlpha Protocol project. 
Phase 1 (Smart Contracts + 4 Arb Scanners) is 100% complete and working perfectly.

[GOAL 1: MiroFish REAL Core Integration (No Mocking!)]
William has explicitly requested to integrate the REAL core logic of MiroFish (https://github.com/666ghj/MiroFish) instead of a mock function. 
MiroFish's core value is generating diverse personas and running multi-agent interviews/consensus using Zep for memory and an LLM for reasoning.

Tasks in `agent/`:
1. Update `agent/requirements.txt` to include:
   camel-oasis==0.2.5
   camel-ai==0.2.78
   zep-cloud==3.13.0
   openai>=1.0.0
   python-dotenv>=1.0.0

2. Create `agent/mirofish_integration.py`. This file MUST implement:
   - A function `generate_trader_personas(market_question, count=5)` that uses the LLM (via OpenAI SDK) to generate 5 distinct quantitative trader personas (e.g., Contrarian, Trend Follower, Value Investor, Macro Analyst, On-Chain Sleuth).
   - A function `setup_zep_memory(personas, market_context)` that uses `zep-cloud` to create users/sessions and inject the market context into their long-term memory.
   - A function `get_mirofish_swarm_consensus(market_question, market_context)` that:
     a) Retrieves memory for each persona from Zep.
     b) Calls the LLM for each persona, asking them to vote YES/NO with a confidence score (0-100) based on their persona and memory.
     c) Aggregates the votes into a probability-weighted consensus score (0.0 to 1.0).
     d) Returns the score and the detailed interview logs.

3. Update `agent/pm_arb_agent.py`:
   - Import `get_mirofish_swarm_consensus` from `mirofish_integration.py`.
   - Integrate it into the main loop: If `scan_yes_no_arb()` finds no opportunities, call the swarm consensus. If consensus > 0.8, log a "SWARM_STRONG_BUY" signal.
   - Ensure graceful fallback if Zep or LLM API fails.

[GOAL 2: UI Upgrade to EdgeBuild Aesthetic]
Our current UI is a basic dark mode. Upgrade it to look exactly like the EdgeBuild platform — a professional, high-end quantitative trading terminal.

Key EdgeBuild Design Language to implement in `frontend/src/`:
1. Color Palette: Deep black background (`#000000` or `#050505`), stark white text, and a signature Neon/Acid Green (`#ccff00` or `#a3e635`) for primary accents.
2. Typography: Use a highly technical, sans-serif font (like Inter) mixed with monospace (JetBrains Mono) for all numbers and code blocks.
3. Layout: "Bento box" style grid layouts. Sharp corners (no rounded borders), thin 1px gray borders (`border-gray-800`), and subtle glowing effects on hover.
4. Specific Component Updates:
   - `PALPHAHubPage.js`: Redesign governance proposals to look like terminal logs.
   - `BacktestPage.js`: Update metric cards to have neon green accent on top borders.
   - `VaultPage.js`: Make the TVL and APY numbers massive and bold.
   - `SwarmPanel.js` (NEW): Create a new component to display the output of the MiroFish swarm consensus (show the 5 personas, their votes, and the aggregated score).

[EXECUTION INSTRUCTIONS]
1. DO NOT use mock data for the MiroFish integration. The Python code MUST make real API calls to OpenAI and Zep.
2. The `.env` file in the project root already contains `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL_NAME` (GLM-4), and `ZEP_API_KEY`. Read these dynamically.
3. Implement the Python logic first, then update the React frontend.
4. When done: `git add -A && git commit -m "feat: integrate real MiroFish swarm logic with Zep and upgrade UI to EdgeBuild" && git push origin main`
```
