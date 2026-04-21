# 🧠 PolyAlpha — Complete Master Document
### AI-Driven Prediction Market Vault | ISOM3270 + Startup Route
**Version:** 2.0 | **Last Updated:** April 1, 2026 | **Author:** William Yong (HKUST RMBI Y2)
**⚠️ FOR NEXT AI: This is the full context handoff. Read ALL sections before responding.**

---

## 📌 TABLE OF CONTENTS
1. [Full Context Memory — Who William Is](#1-full-context-memory)
2. [Project Brief — PolyAlpha One-Liner](#2-project-brief)
3. [AI Tools — How to Use Each One](#3-ai-tools-guide)
4. [Resource Library — GitHub, X, Websites, Threads](#4-resource-library)
5. [Complete Roadmap — Phase 1/2/3](#5-complete-roadmap)
6. [Master To-Do List — Week by Week](#6-master-to-do-list)
7. [Weekly Progress Template (Notion-ready)](#7-weekly-progress-template)
8. [Strategy Research Notes — BTC 15m / 5m](#8-strategy-notes)
9. [Architecture Reference](#9-architecture-reference)
10. [Open Source Integration Plan](#10-open-source-plan)

---

## 1. FULL CONTEXT MEMORY
> **⚠️ FOR NEXT AI:** William wants you to READ this section fully. He changes between AI tools frequently due to context limits. This is the handoff document.

### 👤 Who William Is
- **Name:** William Yong | **School:** HKUST RMBI Year 2, Math Minor
- **Course:** ISOM3270 Blockchain Programming in Business Applications
- **Professor:** James Lei (zblei@ust.hk) — has already **approved** the PolyAlpha project
- **Presentation Date:** May 8, 2026 (Week 12)
- **Current Week:** Week 8 (post-midterm, April 2026). ~5 weeks left to present.

### 🎯 William's Goals (In Priority Order)
1. **Personal income stream** — Actually earn money from the BTC 15m/5m Polymarket strategy
2. **Impress Prof. Lei** — Be seen as the best student, potentially get collaboration/job offer
3. **Course grade A+** — Pass all evaluation criteria cleanly
4. **Future startup route** — HK Web3 Ideathon, Cyberport incubation post-May

### 💡 William's Trading Insights (Core Alpha Hypotheses)
**Insight 1 — BTC 15-Min Opening Signal:**
> "In BTC 15m Polymarket markets, after the opening candle's 7th minute, if the trend from the 1-hour chart is dominant (either clear up or down), there is a 10%+ edge visible at that point. The market is near 50/50 at open but corrects toward 60-65%+ within 7 minutes."

**Insight 2 — NBA 3rd Quarter Lead Strategy:**
> "When a team leads by 10+ points entering the 3rd quarter mid-section, their win probability is 80–90%. Polymarket often shows this at 80-90% odds. The edge per bet is ~8% average. With sufficient capital, this compounds: (1+0.08)^n."

**Insight 3 — The 5-Minute BTC Market (NEW, Feb 2026):**
> Polymarket launched 5-minute BTC Up/Down markets on Polygon in Feb 2026. These generated $650K in Polygon sequencer revenue in 48 hours. This is the CORE market for William's strategy.

### 🛠️ William's Technical Profile
| Skill | Level | Notes |
|---|---|---|
| Python (API calls) | ✅ Can do with little help | Main dev language |
| Solidity / ERC-20 | 🟡 Basic + AI help needed | Never fully deployed solo |
| Polygon testnet deploy | 🟡 Needs guide | Has done StuBase before |
| Backtest scripts | 🟡 Needs AI to scaffold | Can modify once given |
| GitHub (Fork, push, pull) | ✅ Comfortable | Uses Fork app (GUI) |
| React dashboard | 🟡 Needs scaffold | Manus Pro can build this |
| Data visualization | 🟡 Needs AI help | Python + Plotly |

### 🧰 William's Tools
| Tool | Tier | Primary Use |
|---|---|---|
| Claude Pro (Claude Code) | Pro | Code writing, Solidity, architecture design |
| Manus Pro AI | Pro | Website/dashboard scaffold, long-form agent tasks |
| Perplexity Pro | Pro | Research, citations, real-time web search |
| Monica AI Max | Max | Quick Q&A, document summarization |
| Gemini CLI | Free (60 req/min) | Backup model, large context, backtest code |
| GitHub Student Pack | Free | Copilot, private repos, deployment tools |

### 📚 William's Previous Work
- **StuBase:** Full-stack Web3 dApp on Polygon L2, includes ERC-20, Soulbound Tokens, ZK proofs, IPFS, AI classifier, DAO governance — built solo in 1 month
- **Lost HKD 70-80K in crypto** — origin story, motivation for building this
- **Manual Polymarket experience** — traded NBA and BTC markets

### ⚠️ Key Constraints
- **Scope:** No live mainnet execution for course prototype (testnet + paper trading only)
- **Build order (Prof. Lei mandate):** Vault → AI Agent → Dashboard (never skip this order)
- **Time:** ~8 hours/week minimum, up to 14 hours if needed
- **Budget:** $0–50 USD for API/compute
- **Development philosophy:** Use open-source repos, modify + combine, NOT build from scratch

---

## 2. PROJECT BRIEF

### PolyAlpha — One Liner
> **PolyAlpha is an AI-driven on-chain vault that systematically exploits structural price inefficiencies in Polymarket's BTC 5m/15m Up/Down markets using rule-based signal generation, Kelly-sized position logging, and immutable smart contract audit trails — making prediction market alpha trustless, transparent, and fee-distributable.**

### What Version 1 (Course MVP) Delivers
| Component | Description | Status |
|---|---|---|
| `PolyAlphaVault.sol` | ERC-4626 vault on Polygon Amoy testnet | 🔲 To Build |
| `logPosition()` | On-chain immutable AI decision event | 🔲 To Build |
| Python AI Agent | Scans BTC 15m markets, applies 2-rule signal | 🔲 To Build |
| Backtest Module | Historical BTC 15m data → P&L simulation | 🔲 To Build |
| React Dashboard | TVL, position log, simulated P&L | 🔲 To Build |
| Presentation Deck | 10 slides, May 8 demo | 🔲 To Build |
| Project Report | ~3000 words, architecture + business case | 🔲 To Build |

---

## 3. AI TOOLS GUIDE
> **How to use each tool at maximum effectiveness for this project**

### 🟣 Claude Pro (claude.ai + Claude Code)
**Best for:** Solidity writing, Python agent logic, architecture, code review, Remix debugging

**How to use:**
- Use **Claude Code** (terminal) for: writing the full vault contract, scaffolding the Python agent, connecting ethers.js to dashboard
- Use **Claude.ai chat** for: architecture decisions, explaining Solidity errors, writing report sections
- **Prompt template for code tasks:**
```
You are an expert Solidity + Python developer. I'm building PolyAlpha, a BTC prediction market vault on Polygon Amoy testnet.

Context: [paste relevant code or error]
Task: [specific thing you want]
Constraints: [Solidity ^0.8.20, OpenZeppelin, Python 3.11, no live execution]
Output: [production-ready code with inline comments]
```
- **Best use case right now:** Writing `PolyAlphaVault.sol`, writing the Python signal agent

---

### 🟠 Manus Pro AI
**Best for:** Long autonomous tasks, building the React dashboard, generating full project scaffolds, running multi-step research

**How to use:**
- Assign it to: **build the entire React dashboard** (give it the design spec, let it work)
- Assign it to: **scaffold the Python backtest module** from an existing GitHub repo
- Assign it to: **generate the full project report** from bullet points
- **Prompt template:**
```
Task: Build a React dApp dashboard for PolyAlpha vault.
Requirements:
- Page 1: Vault TVL, user shares, deposit/withdraw (connects to testnet contract)
- Page 2: AI Position Log table (reads on-chain PositionLogged events)
- Page 3: Backtested P&L chart (simulated, from JSON file)
- Stack: React + ethers.js + wagmi + Tailwind CSS
- Wallet: MetaMask connect
- Contract address: [to be filled]
Output: Full working codebase
```
- **Best use case right now:** React dashboard, project report, presentation slide content

---

### 🔵 Perplexity Pro
**Best for:** Real-time research, citations, finding GitHub repos, competitive analysis, academic papers

**How to use:**
- Use for: researching latest Polymarket bot strategies, finding exploitable patterns in BTC 15m data
- Use for: finding academic papers on favorite-longshot bias, Kelly criterion variants
- Use for: generating citations for the project report
- Use for: monitoring new open-source Polymarket repos
- **Prompt template:**
```
Search: [specific thing]
Context: I'm building PolyAlpha, an AI trading vault for Polymarket BTC 15-minute markets.
Return: Key findings + GitHub links + academic citations where possible
```
- **Best use case right now:** This document's research, finding backtest data sources

---

### 🟡 Monica AI Max
**Best for:** Quick document summarization, translating technical concepts to business language, proofreading report

**How to use:**
- Use for: summarizing long GitHub READMEs to extract what's useful
- Use for: translating technical architecture into plain language for report
- Use for: proofreading proposal text in English/Chinese
- Use for: quick "explain this error" during development
- **Best use case right now:** Report writing assistance, translating Chinese/English sections

---

### 🟢 Gemini CLI (Free, High Quota)
**Best for:** Large context tasks, processing big data files, running long backtests analysis

**How to use:**
- Set up: `pip install google-generativeai` or use `gemini` CLI
- Use for: processing large CSV files of Polymarket historical data (big context window)
- Use for: running analysis that requires 1000+ API calls/day (free quota)
- **Best use case right now:** Backtest data processing, analyzing large Polymarket datasets

---

### ⚡ Tool Assignment Matrix (What to Use for Each Task)
| Task | Primary Tool | Backup Tool |
|---|---|---|
| Write Vault.sol | Claude Code | Gemini CLI |
| Write Python agent | Claude Code | Monica |
| Build React dashboard | Manus Pro | Claude Code |
| Run backtest | Claude Code / Gemini CLI | Manus Pro |
| Write report | Manus Pro | Monica |
| Find GitHub repos | Perplexity Pro | Google |
| Explain Solidity errors | Claude.ai | Monica |
| Generate slide content | Manus Pro | Claude.ai |
| Citation research | Perplexity Pro | — |
| Data analysis / chart | Claude Code / Gemini | Manus |

---

## 4. RESOURCE LIBRARY

### 🐙 GitHub Repositories (Open Source — Study, Fork, Modify)

#### 🔴 PRIORITY 1 — Core Polymarket Infrastructure
| Repo | Stars | What It Does | Your Use |
|---|---|---|---|
| [Polymarket/agents](https://github.com/Polymarket/agents) | ⭐⭐⭐ | Official Polymarket AI agent framework (MIT) | **Fork this first. Base of your agent.** |
| [Polymarket/py-clob-client](https://github.com/Polymarket/py-clob-client) | ⭐⭐⭐ | Official Python SDK for CLOB API (read + write) | Use for market data, order book reading |
| [Polymarket/polymarket-cli](https://github.com/Polymarket/polymarket-cli) | 1.1k⭐ | Rust CLI tool, pipe JSON market data | Use for quick market scanning in terminal |
| [Polymarket/ctf-exchange](https://github.com/Polymarket/ctf-exchange) | ⭐⭐ | Official exchange smart contracts | Reference for how orders work on-chain |

#### 🟠 PRIORITY 2 — BTC 15m / 5m Specific Bots (Study Why They Earn/Fail)
| Repo | What It Does | Why Interesting | Your Use |
|---|---|---|---|
| [cakaroni/polymarket-arbitrage-bot-btc-eth-15m](https://github.com/cakaroni/polymarket-arbitrage-bot-btc-eth-15m) | Automated market-making for 15m BTC/ETH | **Exact market you want** | Study and improve |
| [infraform/polymarket-arbitrage-trading-bot](https://github.com/infraform/polymarket-arbitrage-trading-bot) | Dump-and-hedge on 15m BTC/ETH/SOL | Has dump+hedge strategy | Study failure modes |
| [Gabagool2-2/polymarket-trading-bot-python](https://github.com/Gabagool2-2/polymarket-trading-bot-python) | 5-min epoch sniper + spread capture | Near-resolution trading | Study their edge |
| [b1rdmania/polymarket-ai-trading](https://github.com/b1rdmania/polymarket-ai-trading) | GPT-4o + mean reversion, 40+ year research | Academic-style approach | Study calibration |
| [luckeyfaraday/polymarket-bot](https://github.com/luckeyfaraday/polymarket-bot) | Free open-source market-making | General market making | Code reference |

#### 🟡 PRIORITY 3 — Smart Contract & Vault
| Repo | What It Does | Your Use |
|---|---|---|
| [OpenZeppelin/openzeppelin-contracts](https://github.com/OpenZeppelin/openzeppelin-contracts) | ERC-4626, ERC-20, Ownable, ReentrancyGuard | **Import directly in Vault.sol** |
| [MrFadiAi/Polymarket-bot](https://github.com/MrFadiAi/Polymarket-bot) | 4 strategies with A-Z setup guide | Good for strategy comparison |
| [CarlosIbCu/polymarket-kalshi-btc-arbitrage-bot](https://github.com/CarlosIbCu/polymarket-kalshi-btc-arbitrage-bot) | Cross-platform BTC arbitrage (Polymarket + Kalshi) | Cross-platform edge detection |

#### 🟢 PRIORITY 4 — Backtesting + Data
| Repo / Tool | What It Does | Your Use |
|---|---|---|
| Search: "Polymarket historical data" on GitHub | Historical odds CSV files | Backtest your BTC 15m strategy |
| [sapph1re/polymarket-agents](https://github.com/sapph1re/polymarket-agents) | Alternative agent framework | Compare approaches |

---

### 🐦 X (Twitter) — Accounts to Follow
| Account | Why Follow |
|---|---|
| @Polymarket | Official announcements, new market launches |
| @polymarket_news | Market summaries, trending markets |
| @igor_mikerin | Published top 10 Polymarket trader profiles |
| @prexpect | Made $118K from Elon tweet count strategy |
| LucasMeow profile searchers | 95% win rate, systematic crypto-safe strategy |
| @chainlab_fun | Your course lab account |
| Search: "Polymarket alpha" on X | New strategy threads weekly |

---

### 📊 Analytics & Research Websites
| Site | What It Offers | Use For |
|---|---|---|
| [polymark.et](https://polymark.et) | AI-powered analytics, 30+ custom metrics | Market analysis, signal confirmation |
| [launchpoly.com/best](https://launchpoly.com/best) | Curated list of 170+ Polymarket tools | Competitive analysis reference |
| [defiprime.com/definitive-guide-to-the-polymarket-ecosystem](https://defiprime.com/definitive-guide-to-the-polymarket-ecosystem) | 170+ tools guide with bot breakdown | Full ecosystem overview |
| [polytrader.ai](https://polytrader.ai) | AI trading strategy platform | Competitor reference |
| [coinsbench.com](https://coinsbench.com/inside-the-mind-of-a-polymarket-bot-3184e9481f0a) | Deep-dive on Gabagool bot strategy | Learn the 5-min spread strategy |
| [phemex.com/news/article/polymarket-analysis](https://phemex.com/news/article/polymarket-analysis-unveils-six-key-profit-strategies-for-2025-49430) | 95M tx analysis, 6 profit strategies | Strategy validation |
| [wire.insiderfinance.io](https://wire.insiderfinance.io/low-risk-polymarket-strategies-for-retail-traders-e7cd96280f21) | Low-risk retail strategies | Report citations |
| [docs.polymarket.com](https://docs.polymarket.com) | Official Polymarket API docs | Development reference |
| [chainlab.fun](https://chainlab.fun) | Your ISOM3270 lab resources | Course reference |

---

### 🧵 Reddit / Forum Threads
| Thread | Why Useful |
|---|---|
| [r/CryptoCurrency — 14 Polymarket Trading Strategies](https://www.reddit.com/r/CryptoCurrency/comments/1payslv/14_polymarket_trading_strategies/) | Comprehensive strategy list |
| [r/polymarket_bets — Brutally Honest 2026 Analytics Guide](https://www.reddit.com/r/polymarket_bets/comments/1rzrjob/polymarket_analysis_tools_the_brutally_honest/) | Tool comparison guide |
| [r/polygonnetwork — BTC 5m glitch discussion](https://www.reddit.com/r/polygonnetwork/comments/1psaqsk/polymarket_bitcoin_updown_glitch_needs_to_be_fixed_in_tight/) | Edge case you need to know |

---

### 📄 Academic / Research Papers
| Paper / Source | Topic | Use For |
|---|---|---|
| Ottaviani & Sørensen (2010) | Favorite-longshot bias theory | Theoretical foundation |
| Gneiting & Raftery (2007) | Proper scoring rules for calibration | Calibration framework |
| Kelly (1956) | Original Kelly criterion | Position sizing justification |
| Phemex analysis of 95M Polymarket txns | Real-world Polymarket profitability | Hard data for proposal |

---

## 5. COMPLETE ROADMAP

```
核心原則: Vault First → AI Second → Dashboard Third
整合勝於重造 · 驗證勝於幻想 · 先做能活的核心，再做放大的外殼
```

### 🏁 PHASE 1 — Course MVP (Now → May 8, 2026)
**Goal: Deliver a working prototype that convinces Prof. Lei + demonstrates commercial potential**

#### Layer 1: Smart Contract (Vault First) 
**Week 8-9 Priority**
- [ ] Study OpenZeppelin ERC-4626 for 2 hours
- [ ] Write `PolyAlphaVault.sol` in Remix (use Claude Code to scaffold)
  - [ ] USDC deposit → mint vault shares
  - [ ] Withdraw shares → receive USDC proportionally
  - [ ] `logPosition()` event emitter (immutable AI decision log)
  - [ ] 20% performance fee logic (`PERFORMANCE_FEE_BPS = 2000`)
  - [ ] 0.5% management fee logic (`MGMT_FEE_BPS = 50`)
  - [ ] `onlyOwner` access control
  - [ ] `ReentrancyGuard` security
- [ ] Test in Remix: deposit → shares → logPosition → events visible
- [ ] Deploy to Polygon Amoy testnet
- [ ] Verify contract on Amoy PolygonScan
- [ ] Get testnet USDC from Polygon faucet
- [ ] Test full cycle: deposit $100 fake USDC → receive shares → agent logs position → PolygonScan event visible

#### Layer 2: Strategy Research (Do in Parallel with Vault)
**Week 8-9 Priority**
- [ ] **Fork** `cakaroni/polymarket-arbitrage-bot-btc-eth-15m` from GitHub
- [ ] **Fork** `infraform/polymarket-arbitrage-trading-bot` from GitHub
- [ ] **Fork** `Gabagool2-2/polymarket-trading-bot-python` from GitHub
- [ ] **Study each repo:** Why does it earn? Why does it fail? What's the edge?
- [ ] Install `py-clob-client`: `pip install py-clob-client`
- [ ] Run read-only test: fetch current BTC 15m market odds
- [ ] Find/download historical BTC 15m Polymarket data (CSV)
- [ ] **Write backtest script** with Claude Code using historical data
- [ ] Test William's 7-minute BTC signal hypothesis on historical data
- [ ] Record: win rate, average edge, Sharpe ratio, max drawdown
- [ ] Document which strategy performs best

#### Layer 3: AI Agent (AI Second)
**Week 9-10 Priority**
- [ ] Write `agent.py` scaffold (use Claude Code)
  ```python
  scan()        → fetch all active BTC 15m markets from Polymarket
  estimate()    → call OpenAI to estimate true probability
  filter()      → apply 8% edge threshold + liquidity filter
  size()        → apply Quarter-Kelly formula
  log_on_chain() → call vault.logPosition() via web3.py
  monitor()     → check exit conditions every 1 min
  ```
- [ ] Connect `agent.py` to `py-clob-client` for market data
- [ ] Connect `agent.py` to OpenAI API for probability estimation
- [ ] Connect `agent.py` to vault contract via `web3.py`
- [ ] **End-to-end test:** agent scans → detects signal → logs position on Polygon Amoy → visible on PolygonScan
- [ ] Run agent in simulation mode (paper trading, not real money)

#### Layer 4: Dashboard (Dashboard Third)
**Week 10-11 Priority**
- [ ] Use **Manus Pro** to scaffold full React dashboard
  ```
  Page 1: Vault Stats (TVL, shares, simulated APY)
  Page 2: AI Position Log (from on-chain PositionLogged events)
  Page 3: Backtest Results (P&L chart, win rate, Sharpe)
  Page 4: Risk Metrics (max drawdown, Kelly fraction per trade)
  ```
- [ ] Connect dashboard to Polygon Amoy via `ethers.js` / `wagmi`
- [ ] Add MetaMask connect button
- [ ] Add deposit/withdraw UI (calls vault contract)
- [ ] Read `PositionLogged` events and display in table
- [ ] Display backtest P&L as interactive chart (Recharts or Plotly)
- [ ] Deploy dashboard to Vercel (free with GitHub student pack)

#### Layer 5: Report + Presentation
**Week 11-12 Priority**
- [ ] Architecture diagram (4-layer: Data → Strategy → Smart Contract → Interface)
- [ ] On-chain/off-chain data split table (quantitative: ~3.7MB/month on-chain, ~30GB off-chain)
- [ ] 5 Blockchain criteria analysis for PolyAlpha (all 5 met)
- [ ] Tokenomics section: vault share mechanics, fee model
- [ ] Business case: market size ($7B+ monthly volume), competitive gap
- [ ] Future perspectives: Phase 2/3 roadmap
- [ ] 3-minute demo video recording
- [ ] Slide deck (10 slides max, use Manus Pro to generate)
- [ ] Submit via Canvas/course portal before May 8

---

### 🚀 PHASE 2 — Strategy Upgrade (Post May 8)
**Goal: Turn backtest-proven strategy into a real, live, money-generating system**

- [ ] Add real-time news RAG to OpenAI calls (Finnhub, CryptoSlate RSS)
- [ ] Add calibration curve (favorite-longshot bias correction)
- [ ] Upgrade from Quarter-Kelly to Monte Carlo uncertainty-adjusted Kelly
- [ ] Add maker execution (not just taker) via CLOB API
- [ ] Test on multiple markets: BTC 5m, ETH 15m, SOL 15m
- [ ] Add regime detection: "Is this a trending or ranging market?"
- [ ] Build order book depth check (don't trade > 20% of available liquidity)
- [ ] Add cross-platform arbitrage: Polymarket vs. Kalshi BTC price
- [ ] Validate strategy decay: does edge disappear after 3 months?
- [ ] Deploy to mainnet with small real capital ($100–500 personal test)

---

### 🌐 PHASE 3 — Protocol Version (Startup Route)
**Goal: Productize the system into a commercializable Web3 protocol**

#### Protocol
- [ ] Full ERC-4626 vault with complete accounting (not just logging)
- [ ] Fee distribution automation (time-locked, governance-controlled)
- [ ] Multi-agent architecture (separate agents for different markets)
- [ ] On-chain governance for risk parameter updates

#### Product
- [ ] B2C: Web app where users deposit USDC and receive auditable yield
- [ ] B2B: Signal API subscription for family offices / crypto funds
- [ ] White-label dashboard for other prediction market protocols

#### Commercialization
- [ ] Apply to 2026 HK Web3 Ideathon (HKUST / IFEC / Cyberport)
- [ ] Apply to HKUST IRAP grant
- [ ] Target Cyberport Creative Micro Fund (CCMF)
- [ ] Open-source the dashboard, monetize the vault protocol

---

## 6. MASTER TO-DO LIST
> **Week-by-Week Execution Plan** | Current: Week 8 (April 1, 2026)

### ✅ Pre-Conditions (Before Starting Week 8)
- [ ] Fork the 3 target repos to personal GitHub
- [ ] Set up local Python environment (`venv`, install `py-clob-client`, `web3`, `openai`)
- [ ] Open Remix IDE and paste vault skeleton
- [ ] Get Polygon Amoy testnet USDC from faucet
- [ ] Set up Claude Code terminal environment

---

### 📅 WEEK 8 (April 1–6) — VAULT SKELETON + STRATEGY RESEARCH
**Target: Have a deployable vault contract + understand the 3 open-source bots**

#### Smart Contract (3 hours)
- [ ] Open Remix IDE (remix.ethereum.org)
- [ ] Use Claude Code: `"Write me a complete PolyAlphaVault.sol using ERC-4626 with: deposit/withdraw USDC, logPosition() event, 20% perf fee, 0.5% mgmt fee, ReentrancyGuard, Ownable"`
- [ ] Paste into Remix, compile with Solidity ^0.8.20
- [ ] Fix any compilation errors (ask Claude.ai if stuck)
- [ ] Deploy to Polygon Amoy via MetaMask
- [ ] Test deposit 10 fake USDC → receive shares

#### Strategy Research (3 hours)
- [ ] Fork `cakaroni/polymarket-arbitrage-bot-btc-eth-15m` → read README fully
- [ ] Fork `infraform/polymarket-arbitrage-trading-bot` → read README fully
- [ ] Fork `Gabagool2-2/polymarket-trading-bot-python` → read README fully
- [ ] For each: answer these 3 questions:
  - What is the core edge this bot claims?
  - Where does it fail / why does it stop earning?
  - What would William improve?

#### Python Environment (2 hours)
- [ ] `pip install py-clob-client web3 openai pandas numpy`
- [ ] Write 10-line test script: fetch current BTC 15m market from Polymarket
- [ ] Confirm live data is working: print current YES price

---

### 📅 WEEK 9 (April 7–13) — BACKTEST + AGENT SKELETON
**Target: Have backtest results showing whether the 15m strategy has real edge**

#### Backtest (4 hours)
- [ ] Find historical Polymarket BTC 15m data (search GitHub for CSV/API)
- [ ] Use Claude Code to write backtest script:
  - Input: historical odds at T+0, T+7min, resolution
  - Test William's hypothesis: "If at T+7min, price > 60%, bet on that direction"
  - Output: win rate, average edge, cumulative P&L, Sharpe ratio, max drawdown
- [ ] Run backtest on at least 200 historical 15m markets
- [ ] Screenshot / save results (this goes in your report)

#### Agent Skeleton (2 hours)
- [ ] Use Claude Code to write `agent.py` with the 6 functions (scan, estimate, filter, size, log, monitor)
- [ ] Make it run without crashing (data doesn't have to be real yet)
- [ ] Connect `scan()` to real Polymarket API via py-clob-client
- [ ] Test: script runs and prints "Scanning... Found 12 BTC markets"

#### Vault Integration (2 hours)
- [ ] Connect `log_on_chain()` in agent.py to vault contract
- [ ] Use `web3.py` to call `logPosition()` from Python
- [ ] Test: agent detects signal → calls logPosition → see event on PolygonScan Amoy

---

### 📅 WEEK 10 (April 14–20) — END-TO-END INTEGRATION
**Target: Full pipeline working: market scan → AI signal → on-chain log**

#### Agent Full Integration (4 hours)
- [ ] Add OpenAI API call to `estimate()` function
- [ ] Add Kelly sizing to `size()` function
- [ ] Add exit monitoring to `monitor()` function
- [ ] Run agent in simulation mode for 24 hours
- [ ] Log all simulated positions to a JSON file + on-chain

#### Dashboard Start (4 hours)
- [ ] Use Manus Pro: give it full dashboard spec (see spec above in Phase 1)
- [ ] Let Manus build the React scaffold
- [ ] Review and fix: connect to real contract address on Amoy
- [ ] Page 1 working: TVL + shares + deposit button

---

### 📅 WEEK 11 (April 21–27) — POLISH + REPORT
**Target: Demo-ready system + draft report complete**

#### Dashboard Polish (2 hours)
- [ ] Page 2 working: AI Position Log from on-chain events
- [ ] Page 3 working: Backtest P&L chart (Recharts/Plotly)
- [ ] Deploy to Vercel (GitHub student pack = free Pro tier)
- [ ] Record 3-minute demo video (screen record: deposit → agent signal → on-chain log → dashboard update)

#### Report Writing (4 hours)
- [ ] Use Manus Pro to draft full report from this document + backtest results
- [ ] Include: architecture diagram, on-chain/off-chain table, blockchain criteria, tokenomics, business case, future perspectives
- [ ] Use Perplexity Pro for citations (academic + market data)
- [ ] Proofread with Monica AI

#### Slide Deck (2 hours)
- [ ] Use Manus Pro to generate 10-slide deck
- [ ] Slide structure: Problem → Market → Solution → Architecture → Demo → Strategy Results → Business Model → Roadmap → Team → Ask

---

### 📅 WEEK 12 (April 28 – May 8) — FINAL PREP + PRESENTATION
**Target: Present live demo to Prof. Lei, ace the Q&A**

- [ ] Rehearse 10-minute presentation 3 times
- [ ] Prepare Q&A answers for likely Prof. Lei questions:
  - "Why Polygon over Ethereum?"
  - "How do you handle model calibration?"
  - "What's your fee collection mechanism?"
  - "How do you prevent reentrancy attacks?"
  - "What would you do differently in Phase 2?"
- [ ] Have live demo ready on Polygon Amoy testnet
- [ ] Final check: all links work, dashboard live on Vercel
- [ ] **May 8: Present PolyAlpha** 🎓

---

## 7. WEEKLY PROGRESS TEMPLATE (Notion-Ready)
> Copy this every Monday into a new Notion page

```markdown
# PolyAlpha — Week [X] Progress
📅 Date: [date]
🏷️ Phase: [Phase 1 / Phase 2 / Phase 3]
⏱️ Hours This Week: [X hrs]

---

## 🎯 本週目標
- [ ] 
- [ ] 
- [ ]

## ✅ 已完成
- ✅ 
- ✅ 

## 🔴 遇到問題
| Problem | Severity 🔴/🟡/🟢 | Status |
|---|---|---|
| | 🔴 Blocker | |

## 🔀 改動決策
| Originally Planned | Changed To | Reason |
|---|---|---|
| | | |

## 📅 下週計劃
- [ ] 
- [ ] 
- [ ]

## 🙋 需要 AI 幫忙
- [ ] Claude Code: 
- [ ] Manus Pro: 
- [ ] Perplexity: 

## 📊 進度自評
- 🟥 Behind >1 week
- 🟨 Slightly behind, recoverable
- 🟩 On track / ahead

## 🧠 本週 Insight
-  
```

---

## 8. STRATEGY NOTES — BTC 15m / 5m Markets

### 🎯 William's Core Hypothesis (To Be Backtested)

**Hypothesis 1: The 7-Minute Signal**
```
Setup:   BTC 15-minute Up/Down market on Polymarket
         Market opens at ~51/49 (near-random)

Trigger: At T+7 minutes, check:
         - 1-hour BTC trend is strong (>0.5% in one direction)
         - Current 15m candle is in same direction
         - Market price has moved to 60%+ for that direction

Signal:  BUY in the 60%+ direction
Edge:    Expected edge ~8-12% based on William's manual trading experience
Risk:    Market can reverse in last 8 minutes

Kelly f: If p=0.65, b=0.538, f* = (0.65×0.538 - 0.35)/0.538 = 0.30
         Quarter-Kelly = 7.5% of vault per trade
```

**Hypothesis 2: The 5-Minute Epoch Sniper**
```
Based on: Gabagool2-2 bot strategy (CoinsBench analysis)
Setup:   Near end of 5-minute window (T+4 to T+5 minutes)
         Current BTC price close to start price (within 0.05%)

Trigger: Price movement suddenly picks direction in final 30-60 seconds
Signal:  BUY winning direction at >85% (collect near-resolution premium)
Edge:    Near-resolution certainty premium (95%+ outcome already determined)

Risk:    Resolution within seconds, must be automated
         Requires fast execution, not suitable for manual trading
```

**Hypothesis 3: Cross-Platform Arbitrage (Phase 2)**
```
Based on: CarlosIbCu/polymarket-kalshi-btc-arbitrage-bot
Setup:   Polymarket vs Kalshi BTC 1-hour price markets

Trigger: Same BTC price event priced differently on both platforms
Signal:  Buy cheaper, sell equivalent on other platform
Edge:    Pure arbitrage, ~2-5% spread when it appears
Risk:    Platforms close positions simultaneously, API latency
```

### 📊 What to Measure in Backtest
```python
metrics_to_track = {
    "win_rate": "% of trades that were profitable",
    "avg_edge": "Average (outcome - price_paid) per trade",
    "sharpe_ratio": "Risk-adjusted return",
    "max_drawdown": "Largest peak-to-trough loss",
    "kelly_fraction": "Optimal bet size as % of vault",
    "regime_performance": "Performance in trending vs ranging BTC hours",
    "time_of_day_performance": "Best performing hours (NYC open vs Asia session)",
    "liquidity_threshold": "Minimum market volume for reliable pricing"
}
```

### ⚠️ Known Edge Cases to Address
1. **Chainlink Resolution Issue:** Polymarket uses Chainlink oracle for BTC price. There was a known glitch where tight market ranges cause incorrect resolutions (Reddit r/polygonnetwork thread).
2. **Gabagool Strategy Limitation:** The spread capture only works when you can consistently fill both YES and NO at >$1.00 total. During low liquidity, you can't fill both sides.
3. **7-Minute Signal Failure Mode:** During high volatility (e.g., macro news drop), price can whipsaw completely in the last 8 minutes. Need: volatility filter (don't trade if ATR > X).
4. **API Rate Limits:** py-clob-client has rate limits. For high-frequency 5m scanning, may need connection pooling.

---

## 9. ARCHITECTURE REFERENCE

### System Architecture (4 Layers)
```
┌─────────────────────────────────────────────────────┐
│  INTERFACE LAYER (React dApp + Vercel)              │
│  - Vault Dashboard (TVL, shares, APY)               │
│  - AI Position Log (on-chain events)                │
│  - Backtest P&L Chart                               │
│  - MetaMask connect / deposit / withdraw            │
└─────────────────┬───────────────────────────────────┘
                  │ ethers.js / wagmi
┌─────────────────▼───────────────────────────────────┐
│  SMART CONTRACT LAYER (Polygon Amoy Testnet)        │
│  PolyAlphaVault.sol                                 │
│  - ERC-4626: deposit/withdraw/shares                │
│  - logPosition(): immutable AI decision event       │
│  - Performance fee (20%) + Mgmt fee (0.5%)         │
│  - ReentrancyGuard + Ownable + access control      │
└─────────────────┬───────────────────────────────────┘
                  │ web3.py
┌─────────────────▼───────────────────────────────────┐
│  STRATEGY LAYER (Python, runs off-chain)            │
│  agent.py                                           │
│  - scan(): py-clob-client → active BTC 15m markets │
│  - estimate(): OpenAI API → true probability        │
│  - filter(): edge > 8% + volume > $10K             │
│  - size(): Quarter-Kelly, cap at 10% TVL           │
│  - log(): calls vault.logPosition() on-chain       │
│  - monitor(): check exit conditions every 60s      │
└─────────────────┬───────────────────────────────────┘
                  │ py-clob-client API
┌─────────────────▼───────────────────────────────────┐
│  DATA LAYER (Off-chain)                             │
│  - Polymarket CLOB API (live market data)           │
│  - OpenAI API (probability estimation)              │
│  - Historical Polymarket CSVs (backtest)            │
│  - Chainlink BTC/USD oracle (resolution source)     │
└─────────────────────────────────────────────────────┘
```

### On-Chain / Off-Chain Data Split
| Data | Location | Size/Month | Cost/Month | Reason |
|---|---|---|---|---|
| Vault share balances | On-chain | 0.6 MB | $0.06 | Immutable ownership proof |
| AI position records | On-chain | 3 MB | $0.30 | Tamper-proof audit log |
| Fee collection events | On-chain | 0.03 MB | $0.003 | Trustless fee enforcement |
| **TOTAL ON-CHAIN** | | **~3.7 MB** | **~$0.37** | |
| Raw news feed | Off-chain | 30 GB | $0.69 | Bulk text, no trust needed |
| OpenAI inference logs | Off-chain | 7.5 MB | $0.0002 | Compute logs only |
| Historical Polymarket data | Off-chain | 500 MB | $0.01 | Training data |
| Model weights | Off-chain | Static | $0.023 | IP, not verifiable state |
| **TOTAL OFF-CHAIN** | | **~32 GB** | **~$0.72** | **4,400x cheaper** |

---

## 10. OPEN SOURCE INTEGRATION PLAN
> **Philosophy: Study → Extract Edge → Combine → Improve → PolyAlpha**

### How to Extract Value From Each Repo

**Step 1: Read all 3 target repos in 1 session**
Use this prompt with Claude Code or Monica:
```
I'm going to paste the README and main .py file from 3 Polymarket bots.
For each one, extract:
1. Core trading strategy in 2 sentences
2. Why it earns money (the actual edge)
3. Why it eventually fails or earns less
4. Top 3 improvements I could make
5. Code I can reuse directly in PolyAlpha
```

**Step 2: Combine the best parts**
```
cakaroni/btc-15m       → market scanning + order placement structure
infraform/dump-hedge   → hedge strategy for risk management
Gabagool/5m-sniper     → near-resolution premium capture logic
b1rdmania/ai-trading   → OpenAI integration + calibration approach

→ PolyAlpha = best of all four, with on-chain logging added
```

**Step 3: Differentiation — What PolyAlpha Adds**
| Feature | Existing Bots | PolyAlpha Adds |
|---|---|---|
| Market scanning | ✅ Most have this | Same |
| Signal generation | ✅ Rule-based | + OpenAI probability estimation |
| Position sizing | 🟡 Some have Kelly | ✅ Quarter-Kelly with TVL cap |
| On-chain logging | ❌ None | ✅ Immutable audit trail |
| Vault structure | ❌ None | ✅ ERC-4626, fee automation |
| Dashboard | ❌ None | ✅ React + on-chain events |
| Auditability | ❌ Black box | ✅ Every decision on PolygonScan |

---

## 📋 QUICK REFERENCE — Vault Contract Skeleton

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/extensions/ERC4626.sol";
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/access/Ownable.sol";
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/utils/ReentrancyGuard.sol";

contract PolyAlphaVault is ERC4626, Ownable, ReentrancyGuard {

    uint256 public constant PERFORMANCE_FEE_BPS = 2000; // 20%
    uint256 public constant MGMT_FEE_BPS = 50;          // 0.5% annual
    address public aiAgent;

    event PositionLogged(
        address indexed agent,
        string marketQuestion,
        uint256 amountUSDC,
        uint256 impliedOdds,    // scaled by 10000, e.g. 7200 = 72.00%
        uint256 aiProbability,  // scaled by 10000, e.g. 8500 = 85.00%
        string side,            // "UP" or "DOWN"
        uint256 kellyFraction,  // scaled by 10000, e.g. 750 = 7.5%
        uint256 timestamp
    );

    constructor(IERC20 _usdc, address _agent)
        ERC4626(_usdc)
        ERC20("PolyAlpha Vault Share", "paUSDC")
        Ownable(msg.sender)
    {
        aiAgent = _agent;
    }

    modifier onlyAgent() {
        require(msg.sender == aiAgent, "Only AI agent");
        _;
    }

    function logPosition(
        string calldata marketQuestion,
        uint256 amountUSDC,
        uint256 impliedOdds,
        uint256 aiProbability,
        string calldata side,
        uint256 kellyFraction
    ) external onlyAgent {
        emit PositionLogged(
            msg.sender, marketQuestion, amountUSDC,
            impliedOdds, aiProbability, side, kellyFraction, block.timestamp
        );
    }

    function collectPerformanceFee(uint256 profitAmount) external onlyOwner nonReentrant {
        uint256 fee = (profitAmount * PERFORMANCE_FEE_BPS) / 10000;
        // Transfer fee to owner
        IERC20(asset()).transfer(owner(), fee);
    }

    function setAgent(address newAgent) external onlyOwner {
        aiAgent = newAgent;
    }
}
```

---

## 📋 QUICK REFERENCE — Agent Python Skeleton

```python
# agent.py — PolyAlpha AI Signal Agent
import time
from py_clob_client.client import ClobClient
from openai import OpenAI
from web3 import Web3

# Config
POLYMARKET_API = "https://clob.polymarket.com"
EDGE_THRESHOLD = 0.08   # 8% minimum edge
MIN_VOLUME = 10000      # $10K minimum market volume
KELLY_CAP = 0.10        # Max 10% of vault per position
KELLY_FRACTION = 0.25   # Quarter-Kelly

# Clients
poly = ClobClient(POLYMARKET_API)
ai = OpenAI()
w3 = Web3(Web3.HTTPProvider("https://rpc-amoy.polygon.technology/"))

def scan():
    """Fetch active BTC Up/Down 15m markets"""
    markets = poly.get_markets()
    btc_markets = [m for m in markets if "Bitcoin Up or Down" in m.get("question", "")]
    return btc_markets

def estimate(market_question: str, current_odds: float) -> float:
    """Ask OpenAI to estimate true probability"""
    response = ai.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": f"BTC 15-min market: '{market_question}'. Current UP odds: {current_odds:.2f}. Based on current market conditions, what is the TRUE probability of UP? Reply with just a number 0-1."
        }]
    )
    return float(response.choices[0].message.content.strip())

def kelly_size(p: float, odds: float) -> float:
    """Quarter-Kelly position sizing"""
    b = (1 - odds) / odds  # net odds
    q = 1 - p
    f_star = (p * b - q) / b
    return min(max(f_star * KELLY_FRACTION, 0), KELLY_CAP)

def should_trade(market_odds: float, ai_prob: float) -> tuple:
    """Apply trading rules"""
    edge = ai_prob - market_odds
    if abs(edge) < EDGE_THRESHOLD:
        return False, None
    side = "UP" if edge > 0 else "DOWN"
    return True, side

def log_on_chain(market_q, amount, odds, ai_prob, side, kelly_f):
    """Log position to vault smart contract"""
    # vault.logPosition(marketQ, amount, odds*10000, aiProb*10000, side, kellyF*10000)
    pass  # Complete with actual contract call

def run_agent():
    print("PolyAlpha Agent Starting...")
    while True:
        markets = scan()
        for market in markets:
            odds = float(market.get("bestAsk", 0.5))
            ai_prob = estimate(market["question"], odds)
            trade, side = should_trade(odds, ai_prob)
            if trade:
                kelly_f = kelly_size(ai_prob, odds)
                print(f"SIGNAL: {side} | Edge: {ai_prob-odds:.2%} | Kelly: {kelly_f:.2%}")
                log_on_chain(market["question"], 100, odds, ai_prob, side, kelly_f)
        time.sleep(60)

if __name__ == "__main__":
    run_agent()
```

---

## 🔑 FINAL REMINDERS (Print These)
1. **Build Order: VAULT → AI AGENT → DASHBOARD. Never skip.**
2. **Vault done = passing grade. AI + Dashboard = A+ grade.**
3. **No live mainnet funds for course prototype. Testnet only.**
4. **Use Manus Pro for dashboard, Claude Code for contracts/Python.**
5. **You are the infrastructure builder, not the trader. PolyAlpha is the shovel.**
6. **Send Prof. Lei a progress update at Week 9 and Week 11.**
7. **If stuck > 2 hours, ask Claude Code. Never debug alone for > 2 hours.**

---
*Document created: April 1, 2026 | PolyAlpha v2.0 Master Plan*
*Next AI reading this: All context above is current and accurate as of this date.*


---

# 🔧 CONTINUATION — April 1 Execution Plan


---

## Step 3 — 研究 3 個 Repo（30 分鐘）

### 如何拆解每一個 Repo（用 Monica AI Max）

**Repo 1: `cakaroni/polymarket-arbitrage-bot-btc-eth-15m`**
- 核心策略：BTC/ETH 15 分鐘 Up/Down epoch sniper
- 為什麼賺錢少：只做 entry，沒有 dynamic exit（價格 60% → 75% 時應該 EXIT，不等 resolution）
- 你的優化點：加入 7 分鐘入場信號 + 15% gain exit trigger（你自己的交易觀察）

**Repo 2: `infraform/polymarket-arbitrage-trading-bot`**
- 核心策略：YES + NO price sum < $0.97 時做 unity arbitrage
- 為什麼賺錢少：gas fee + Polymarket 2% 的 resolution fee 吃掉大部分 edge
- 你的優化點：設 threshold > 3%，不做 < 2.5% 的機會

**Repo 3: `Gabagool2-2/polymarket-trading-bot-python`**
- 核心策略：基於 orderbook depth 做 scalping
- 為什麼賺錢少：在 low-liquidity 市場 spread 大，難以 fill
- 你的優化點：只做 volume > $50K 的 BTC 市場，避免 thin liquidity

---

## 你的 BTC 15m 三個核心策略假設（Backtest 重點）

### 假設 1：7 分鐘動量信號
```
條件：
- 開盤後第 7 分鐘，BTC 已有明確方向（上/下 0.3% vs 15 分鐘開盤價）
- Polymarket 對應市場仍然在 50-55% 附近（市場尚未 price in）
- 這時候 YES/NO 的真實概率已經接近 70-80%
行動：買 YES（如果 BTC 在漲）或 NO（如果 BTC 在跌）
Exit：當 position 達到 70%+ 或在第 12 分鐘（不等 resolution）
```

### 假設 2：Kelly Criterion 自動倉位管理
```python
def kelly_fraction(p_estimated, market_odds):
    b = (1 - market_odds) / market_odds  # net odds
    q = 1 - p_estimated
    f_star = (p_estimated * b - q) / b
    half_kelly = f_star * 0.5
    return min(max(half_kelly, 0), 0.10)  # Cap at 10% of vault
```

### 假設 3：跨市場 Unity Arbitrage（BTC 15m）
```
條件：
- BTC 15m UP YES + DOWN NO 的合計 < $0.97
- 換算 edge = $0.03 - 2% fee = $0.01 per share（1% 純利）
- 需要 > 3% gap 才值得（考慮 gas）
行動：同時買 YES + NO
Exit：市場 resolution 後自動結算
```

---

## 完整 AI 工具使用分工表

| 工具 | 最佳使用場景 | 具體怎麼用 |
|---|---|---|
| **Claude Pro / Claude Code** | 寫代碼、Debug、Solidity 合約 | 直接貼錯誤信息，說「fix this」；用 Claude Code 生成完整模塊 |
| **Manus Pro AI** | 建 Website / Dashboard / Prototype UI | 「Build me a React dashboard that reads events from this contract ABI...」|
| **Perplexity Pro** | 實時市場研究、資源查找、競爭分析 | 你現在用的就是這個 — 搜索策略、找 repo、比較工具 |
| **Monica AI Max** | 長文件分析、多 repo 對比、翻譯報告 | 把 3 個 repo README 全貼進去，問「比較優劣+改進方向」|

### Claude Code 的最強 Prompt 模板
```
你是一個 Web3 developer，幫我：
1. [具體任務]
2. 使用 [framework/library]
3. 輸出要求：[可直接運行的代碼，加上簡短的 inline comments]
4. 不要解釋，直接給 code
```

### Manus Pro 建 Dashboard 的 Prompt
```
Build a Next.js dashboard for PolyAlpha with:
- Left sidebar: Vault TVL, My shares, APY
- Main area: Position log table (timestamp, market, side, AI prob, market odds, edge)
- Pull data from this Ethereum contract ABI: [貼你的 ABI]
- Connect to MetaMask
- Dark mode default
- Deploy-ready (no backend required)
```

---

## 資源庫 / 資料庫（完整版）

### 🔴 必看 GitHub Repos（可直接 Fork + 改）
| Repo | Stars | 用途 |
|---|---|---|
| `cakaroni/polymarket-arbitrage-bot-btc-eth-15m` | ~200 | 你的主要 base strategy |
| `infraform/polymarket-arbitrage-trading-bot` | ~150 | Unity arbitrage 參考 |
| `Gabagool2-2/polymarket-trading-bot-python` | ~100 | Python API 架構 |
| `Polymarket/agents` | ~800 | 官方 AI agent framework |
| `OpenZeppelin/openzeppelin-contracts` | 24k+ | ERC-4626 vault 標準 |
| `Polymarket/py-clob-client` | ~500 | 官方 Python SDK |

### 🟡 X（Twitter）必追帳號
| 帳號 | 追蹤原因 |
|---|---|
| @betmoardotfun | Polymarket 最大工具，看 whale 動向 |
| @PolyAlertHub | 實時 alert，了解市場異動 |
| @Polysights | AI 市場分析 |
| @polybroapp | 自律 AI trading agent（競品研究）|
| @PolymarketBuild | 官方 builder 更新 |
| @HashDive | Smart Score 分析 |

### 🟢 整好的網站（直接用）
| 網站 | 用途 |
|---|---|
| defiprime.com/definitive-guide-to-the-polymarket-ecosystem | 170+ 工具完整地圖（你剛找到的）|
| polymark.et | 最完整的工具目錄 |
| polymarket.com/leaderboard | 看 top whale 的策略 |
| polysights.com | AI 分析 + arbitrage detection |
| hashDive.io | Smart Score + wallet tracking |
| eventarb.com | 跨平台套利計算器 |
| docs.polymarket.com | 官方 API 文檔 |
| remix.ethereum.org | Solidity 開發環境 |

### 🔵 論文 / 研究（Prof. Lei 喜歡看到你引用）
- IMDEA Networks: "Automated Market Making in Polymarket" (2024) — $40M arbitrage study
- Kelly Criterion: "A New Interpretation of Information Rate" (Kelly, 1956) — 你的倉位管理公式來源
- ERC-4626: EIP-4626 specification (ethereum.org/eips/eip-4626)

---

## 給 Prof. Lei 的進度更新 Email（Week 8 版本，今週可以用）

```
Subject: PolyAlpha Progress Update — Smart Contract Deployed on Testnet

Dear Prof. Lei,

Following your guidance from last time, I've been making steady progress on PolyAlpha this week.

Key milestones:
1. Vault contract (ERC-4626 with logPosition() event) deployed on Polygon Amoy testnet
   Contract address: [your address here]
   PolygonScan: [link]

2. Python agent connected to Polymarket's read API:
   - Scanning BTC 15m Up/Down markets in real-time
   - Applying 2 simple rules: 8% edge threshold + half-Kelly sizing

3. Initial backtest framework under construction:
   - Testing the "7-minute momentum signal" hypothesis on historical BTC/Polymarket data

Next milestone: Full end-to-end test (agent finds signal → logs position on-chain)

I'll have a brief demo video ready by [date]. Let me know if you'd like to chat before the final presentation.

Best regards,
William Yong
```

---

## Week 8–12 完整執行計劃（逐週）

### Week 8（本週，April 1–7）
- [x] Fork 3 repos
- [ ] Python env setup + py-clob-client 安裝
- [ ] test_connection.py 成功掃描 BTC 15m 市場
- [ ] PolyAlphaVault.sol 在 Remix 編譯通過
- [ ] 部署到 Polygon Amoy testnet
- [ ] logPosition() 第一次 on-chain event

### Week 9（April 8–14）
- [ ] Python agent skeleton: scan() → estimate() → filter() → log_on_chain()
- [ ] 整合 OpenAI API（或免費 Gemini CLI）做概率估算
- [ ] Backtest 框架：跑 30 天歷史 BTC 15m 數據
- [ ] 測試 7 分鐘信號假設（勝率是否 > 60%？）
- [ ] 給 Prof. Lei 發第一封進度 email

### Week 10（April 15–21）
- [ ] 用 Manus Pro 建 React Dashboard
- [ ] 接 ethers.js 讀取 on-chain 的 PositionLogged events
- [ ] 顯示：TVL、策略績效、position log table
- [ ] Backtest 結果可視化（equity curve）
- [ ] 中期 demo 視頻（3 分鐘）

### Week 11（April 22–28）
- [ ] 全端 end-to-end 測試：agent → vault → dashboard → on-chain
- [ ] Report 初稿（架構圖、業務邏輯、on/off-chain split）
- [ ] Tokenomics 章節（vault shares、performance fee、management fee 設計）
- [ ] ReentrancyGuard + access control security review
- [ ] PPT 大綱 8 頁

### Week 12（April 29 – May 8 Final Presentation）
- [ ] PPT 完成（12 張）
- [ ] Live demo 練習 3 次
- [ ] Report final version
- [ ] Prepare "startup pitch" mode answer for Prof. Lei's Q&A
- [ ] Submit on May 8 🎯

---

## 完整進度表（給下一個 AI 的 Context）

```
截至 April 1, 2026 的狀態：
✅ Proposal 已批准（Prof. Lei greenlighted）
✅ 項目定義：PolyAlpha v1 = BTC 15m策略 + ERC-4626 vault + AI agent + React dashboard
✅ 工具確認：Claude Pro + Manus Pro + Perplexity Pro + Monica Max
✅ Strategy：7分鐘動量信號 + Kelly sizing + Unity arbitrage
❌ Smart contract：尚未部署（今晚目標）
❌ Python agent：尚未運行（本週目標）
❌ Dashboard：尚未建（Week 10 目標）
❌ Backtest：尚未完成（Week 9 目標）
Final Presentation：May 8, 2026
```
