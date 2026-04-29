# PolyAlpha Protocol — Phase 2: EdgeBuild UI & MiroFish Integration

**執行方式：**
請將以下內容**全部複製**，直接貼進 VS Code 終端機的 Claude Code 中執行。

---

```text
[ROLE & CONTEXT]
You are an expert Web3 Frontend Developer and AI Architect. We are entering Phase 2 of the PolyAlpha Protocol project. 
Phase 1 (Smart Contracts + 4 Arb Scanners) is 100% complete and working perfectly.

[GOAL 1: UI Upgrade to EdgeBuild Aesthetic]
Our current UI is a basic dark mode. I want to upgrade it to look exactly like the EdgeBuild platform (edgebuild.com) — a professional, high-end quantitative trading terminal.

Key EdgeBuild Design Language to implement in `frontend/src/`:
1. Color Palette: Deep black background (`#000000` or `#050505`), stark white text, and a signature Neon/Acid Green (`#ccff00` or `#a3e635`) for primary accents, buttons, and positive metrics.
2. Typography: Use a highly technical, sans-serif font (like Inter or Space Grotesk) mixed with monospace (JetBrains Mono) for all numbers and code blocks.
3. Layout: "Bento box" style grid layouts. Sharp corners (no rounded borders), thin 1px gray borders (`border-gray-800`), and subtle glowing effects on hover.
4. Specific Component Updates:
   - `PALPHAHubPage.js`: Redesign the governance proposals to look like terminal logs or code commits.
   - `BacktestPage.js`: Update the metric cards to have the neon green accent on top borders, and use monospace for all numbers.
   - `VaultPage.js`: Make the TVL and APY numbers massive and bold.

[GOAL 2: MiroFish Swarm Intelligence Integration]
Currently, our Agent relies on simple momentum and Kelly sizing. We want to integrate the core concept of MiroFish (https://github.com/666ghj/MiroFish) — Swarm Intelligence Prediction.

Task in `agent/pm_arb_agent.py`:
1. Create a new dummy/mock function `get_mirofish_swarm_consensus(market_id)` that simulates asking 5 different AI personas (e.g., "The Contrarian", "The Trend Follower", "The Value Investor", "The Macro Analyst", "The On-Chain Sleuth") for their prediction on a market.
2. It should return a probability-weighted consensus score (0.0 to 1.0).
3. Integrate this into the main loop: If the `scan_yes_no_arb()` finds no opportunities, fallback to checking the MiroFish consensus. If consensus > 0.8, log a "SWARM_STRONG_BUY" signal.
4. This is a V1 stub to prepare for the actual Python multi-agent integration later.

[EXECUTION INSTRUCTIONS]
1. Update the React components (`VaultPage`, `BacktestPage`, `PALPHAHubPage`, `App.js`) to apply the EdgeBuild CSS classes.
2. Add the MiroFish stub to `pm_arb_agent.py`.
3. Test the React build locally to ensure no compilation errors.
4. When done: `git add -A && git commit -m "feat: upgrade UI to EdgeBuild aesthetic and add MiroFish swarm stub" && git push origin main`
```
