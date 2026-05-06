# PolyAlpha Protocol — Revised Pitch Deck Prompts (v2)

> **修改說明**：根據 William 的逐頁審閱意見，以下為所有需要重新生成的頁面之新版 Prompt。
> 每頁都標明了「修改內容摘要」，方便你快速確認。
> 確認後，Manus 將批量重新生成這些頁面並更新 PPTX。

---

## 新增頁面

### SLIDE 1.5 — Agenda（封面與問題之間新增）

**修改摘要**：在封面與 Slide 2 之間新增 Agenda 頁。

```
Generate a 16:9 widescreen pitch deck slide. Dark cyberpunk terminal aesthetic. Black background (#0a0a0a), neon green (#ccff00) accents, white monospace text.

LAYOUT:
- Top left: "AGENDA //" in neon green small caps
- Center: A vertical numbered list of agenda items, each as a clean row with a neon green number badge on the left and white text on the right:
  01 → Problem Definition
  02 → Market Opportunity
  03 → Solution Overview
  04 → How It Works
  05 → Alpha Engine Mechanism
  06 → Live Demonstration
  07 → Technical Architecture
  08 → Security Model
  09 → Tokenomics
  10 → Open-Source Integration
  11 → Competitive Landscape
  12 → Strategy Validation
  13 → Business Model
  14 → Roadmap
  15 → Conclusion & Q&A
- The currently highlighted item (none — this is the intro) has no highlight.
- Right side (30%): A vertical neon green glowing line with small dot markers at each agenda item position, like a progress indicator.
- Bottom: Small gray text "ISOM3270 Final Project · William Yong · 2026"
Style: Clean, minimal, professional. The numbered list is the hero element.
```

---

## 修改頁面

### SLIDE 1 — Cover（封面）

**修改摘要**：
1. 頁腳年份從 "2025" 改為 "2026"（現在是 2026 年）
2. 移除 "here"、"mems"、"what" 等手寫標記

```
Generate a 16:9 widescreen pitch deck slide. Dark cyberpunk terminal aesthetic. Black background (#0a0a0a), neon green (#ccff00) accents, white monospace text.

LAYOUT:
- Top left corner: Small neon green badge "ISOM3270 FINAL PROJECT"
- Center-left (60% width):
  Line 1 (neon green, large monospace): "POLYALPHA"
  Line 2 (white, massive bold): "PROTOCOL"
  Line 3 (neon green, medium): "AI × DeFi × Prediction Markets"
  Line 4 (white, small): "An autonomous AI-driven vault for decentralized prediction market arbitrage"
  Below: Two neon green status badges side by side:
    [⬡ TESTNET LIVE]    [▶ PAPER TRADING ACTIVE]
- Center-right (40% width): A dark terminal window mockup showing a simplified dashboard screenshot:
  Terminal title bar: "polyalpha-dashboard.vercel.app"
  Inside: Green text showing mock trading signals and vault TVL numbers
- Bottom bar (full width, dark gray):
  Left: "github.com/YongWilliam-ai/polyalpha-protocol"
  Center: "polyalpha-dashboard.vercel.app"
  Right: "ISOM3270 Final Project · William Yong · 2026"
Style: Impactful cover slide. The two-column layout balances text and visual. Clean, no hand-written annotations.
```

---

### SLIDE 2 — Problem Definition（問題定義）

**修改摘要**：
1. 頂部新增 section 標題標籤 `[Problem Definition]`，原有白色粗體標題保留但移至副標題位置
2. 底部新增 "Source: Polymarket Analytics 2025, Grand View Research" 引用行

```
Generate a 16:9 widescreen pitch deck slide. Dark cyberpunk terminal aesthetic. Black background (#0a0a0a), neon green (#ccff00) accents, white monospace text.

LAYOUT:
- Top left: Small neon green section label "[Problem Definition]"
- Below section label: White bold large title: "Prediction markets are broken for retail — speed, data, and capital create an impossible barrier"
- CENTER: A large inverted triangle (funnel shape) divided into 3 horizontal layers, each with a dark background and neon green left border:
  TOP LAYER (widest, dark red tint):
  Icon: ⚡ lightning bolt
  Title: "NO SPEED"
  Text: "Retail users cannot react to order book changes in milliseconds. Institutional bots dominate price discovery."
  MIDDLE LAYER (medium width, dark orange tint):
  Icon: 📊 chart
  Title: "NO DATA"
  Text: "Real-time CLOB data, sentiment feeds, and cross-market signals require expensive infrastructure."
  BOTTOM LAYER (narrowest, dark yellow tint):
  Icon: 💰 money bag
  Title: "NO CAPITAL"
  Text: "Minimum viable arbitrage requires $10,000+ to overcome gas fees and slippage."
- RIGHT SIDE: Three data stat cards stacked vertically:
  Card 1: "$220B" (neon green large) / "Polymarket 2025 Trading Volume" (white small)
  Card 2: "97.5%" (neon green large) / "Market share: Polymarket + Kalshi" (white small)
  Card 3: "0" (neon green large) / "Institutional-grade retail tools available" (white small)
- BOTTOM: Thin gray line, then small gray citation text: "Sources: Polymarket Analytics 2025 · Grand View Research · KuCoin Research"
Style: Problem-focused, urgent visual hierarchy. The inverted triangle is the hero element.
```

---

### SLIDE 3 — Market Opportunity（市場機會）

**修改摘要**：
1. 頂部新增 section 標題標籤 `[Market Opportunity]`
2. Bar chart 時間軸更新：2025 為實際數據（非 est），2026 為 est，2030 為 Proj
3. 數據更新：2024=$15.8B, 2025=$63.5B（實際）, 2026=$120B（est）, 2030=$500B（Proj）
4. 底部句子補全：改為 "Despite $220B in Polymarket 2025 trading volume, zero institutional-grade automated arbitrage tools exist for retail investors."

```
Generate a 16:9 widescreen pitch deck slide. Dark cyberpunk terminal aesthetic. Black background (#0a0a0a), neon green (#ccff00) accents, white monospace text.

LAYOUT:
- Top left: Small neon green section label "[Market Opportunity]"
- Below section label: White bold large title: "Prediction markets grew 302% in 2025 — the arbitrage infrastructure layer is still empty"
- LEFT SIDE (55%): A bar chart titled "Global Prediction Market Volume":
  X-axis: Years 2022, 2023, 2024, 2025, 2026, 2030
  Y-axis: Volume in billions ($B)
  Bars with heights:
    2022: $0.8B (gray bar, small)
    2023: $3.3B (gray bar)
    2024: $15.8B (gray bar, labeled "ACTUAL")
    2025: $63.5B (NEON GREEN bar, tallest actual, labeled "ACTUAL ✓")
    2026: $120B (lighter green bar, labeled "(est)")
    2030: $500B (outline-only bar, labeled "(Proj)")
  Above the 2025 bar: "+302% YoY" badge in neon green
  Chart style: Dark grid lines, neon green axis labels
- RIGHT SIDE (45%): Three concentric circle TAM/SAM/SOM diagram:
  Outer circle (dark gray): "TAM: $63.5B — Global Prediction Market Volume (2025)"
  Middle circle (dark green): "SAM: $6.3B — Automated Arbitrage Segment (10%)"
  Inner circle (neon green glow): "SOM: $15M — PolyAlpha Phase 3 Target TVL"
  Below circles: One-line insight in white: "Despite $220B in Polymarket 2025 trading volume, zero institutional-grade automated arbitrage tools exist for retail investors."
- BOTTOM: Small gray citation: "Sources: CoinGecko 2025 Annual Report · Yahoo Finance · Polymarket Analytics"
Style: Data-heavy but clean. Bar chart is the hero. Updated with 2025 actual data.
```

---

### SLIDE 4 — Solution Overview（解決方案概述）

**修改摘要**：頂部新增 section 標題標籤 `[Solution Overview]`，原標題保留為副標題。

```
Generate a 16:9 widescreen pitch deck slide. Dark cyberpunk terminal aesthetic. Black background (#0a0a0a), neon green (#ccff00) accents, white monospace text.

LAYOUT:
- Top left: Small neon green section label "[Solution Overview]"
- Below section label: White bold large title: "PolyAlpha democratizes institutional arbitrage through three interlocking pillars"
- CENTER: Three large vertical card columns side by side, each with a neon green top border and dark background:
  CARD 1 — VAULT:
  Icon: 🏦 (large, neon green)
  Title: "ERC-4626 Vault"
  Subtitle: "On-Chain Asset Management"
  Body: "Deposit USDC. Receive PALPHA shares. Withdraw anytime. 100% non-custodial."
  Bottom badge: "OpenZeppelin v5 · Auditable"
  CARD 2 — AI ENGINE (center, slightly larger, glowing border):
  Icon: 🤖 (large, neon green)
  Title: "AI Alpha Engine"
  Subtitle: "Off-Chain Signal Generation"
  Body: "4-layer signal stack. MiroFish Swarm AI. BitPilot Safety Chain. Empirical Kelly sizing."
  Bottom badge: "62.3% Win Rate · 2.1 Sharpe"
  CARD 3 — DAO:
  Icon: 🗳️ (large, neon green)
  Title: "DAO Governance"
  Subtitle: "Community-Owned Protocol"
  Body: "PALPHA token holders vote on strategy parameters. Buyback-and-burn from profits."
  Bottom badge: "Deflationary · Aligned Incentives"
- BOTTOM: Full-width dark bar with white text: "The result: institutional-grade yield, accessible with $10 minimum deposit, fully transparent on-chain."
Style: Three-pillar card layout. Center card (AI Engine) is the hero with extra glow effect.
```

---

### SLIDE 5 — How It Works（運作流程）

**修改摘要**：
1. 頂部新增 section 標題標籤 `[Solution Workflow — How It Works]`
2. 在流程圖下方新增 Quarter-Kelly 說明框與 20% Circuit Breaker 說明
3. 新增 PolyAlpha vs Traditional Hedge Fund 對比表格

```
Generate a 16:9 widescreen pitch deck slide. Dark cyberpunk terminal aesthetic. Black background (#0a0a0a), neon green (#ccff00) accents, white monospace text.

LAYOUT:
- Top left: Small neon green section label "[Solution Workflow — How It Works]"
- Below section label: White bold title: "From deposit to yield in 6 automated steps — no human intervention required"
- TOP SECTION (60% height): A horizontal 6-node flow diagram:
  NODE 1: 💰 "Investor Deposits USDC" → 
  NODE 2: 🏦 "ERC-4626 Vault mints PALPHA shares" → 
  NODE 3: 🤖 "AI Agent scans Polymarket CLOB" → 
  NODE 4: 📊 "Signal validated by MiroFish Swarm + Kelly" → 
  NODE 5: ⚡ "BitPilot Safety Chain: 6-step check" → 
  NODE 6: 📈 "Trade executed → Profit flows back to Vault"
  Arrows between nodes: thick neon green arrows
  Node 5 has a red warning badge: "CIRCUIT BREAKER: 20% max drawdown"
- BOTTOM SECTION (40% height): Two-column comparison table:
  Left column header: "PolyAlpha Protocol" (neon green)
  Right column header: "Traditional Hedge Fund" (gray)
  Rows:
  Min Deposit | $10 USDC | $1,000,000+
  Transparency | 100% On-Chain | Black Box
  Custody | Non-Custodial | Fund Manager
  Fee Structure | 2/20 (no lock-up) | 2/20 + 2-year lock
  Kelly Fraction | 0.25 (Quarter-Kelly) | Proprietary
  Circuit Breaker | 20% drawdown, hardcoded | Discretionary
  Table style: Dark rows, neon green left column, white right column, alternating row shading
- BOTTOM: Small white footnote: "Quarter-Kelly (kelly_fraction=0.25) reduces max drawdown vs full Kelly while maintaining positive expected value. Circuit breaker hardcoded in PolyAlphaVault.sol — cannot be overridden."
Style: Flow diagram on top, comparison table on bottom. Both are equally important.
```

---

### SLIDE 6 — Alpha Engine Mechanism（Alpha 引擎機制）

**修改摘要**：
1. 頂部新增 section 標題標籤 `[Alpha Engine Mechanism]`
2. 在 Market Input 圖表的最低點標記 "BUY"，最高點標記 "SELL"

```
Generate a 16:9 widescreen pitch deck slide. Dark cyberpunk terminal aesthetic. Black background (#0a0a0a), neon green (#ccff00) accents, white monospace text.

LAYOUT:
- Top left: Small neon green section label "[Alpha Engine Mechanism]"
- Below section label: White bold title: "A 4-layer signal stack ensures we only trade when the mathematical edge is confirmed"
- LEFT SIDE (50%): A vertical 4-layer architecture diagram, each layer as a horizontal dark card:
  LAYER 1 (top): "📡 DATA INGESTION" — Polymarket CLOB API + 6551Team News API + Binance price feed
  LAYER 2: "🧠 SIGNAL GENERATION" — ROC momentum + RSI divergence + MACD crossover + Sentiment score
  LAYER 3: "🤖 SWARM VALIDATION" — MiroFish: 5 AI personas vote independently. Consensus threshold: 60%+
  LAYER 4 (bottom): "⚡ EXECUTION" — Quarter-Kelly sizing → BitPilot Safety Chain → Polymarket order submit
  Downward arrows between layers in neon green
- RIGHT SIDE (50%): A market price chart mockup:
  Title: "Market Input Signal" in neon green
  Chart: A sine-wave-like price line in neon green on dark background
  At the LOWEST point of the wave: A green upward triangle with label "BUY ▲" in bright neon green
  At the HIGHEST point of the wave: A red downward triangle with label "SELL ▼" in red
  Below chart: Two output signal badges:
    [STRONG_BUY: 0.87 confidence] in neon green
    [HOLD: 0.45 confidence] in gray
- BOTTOM: Dark bar with white text: "Only trades when: Swarm consensus ≥ 60% AND Kelly edge > 0 AND all 6 safety checks pass"
Style: Technical but readable. BUY/SELL markers on the chart are prominent and clear.
```

---

### SLIDE 7 — Live Demonstration（前端展示）

**修改摘要**：
1. 頂部新增 section 標題標籤 `[Live Demonstration]`
2. 備註：在此頁後插入 30-45 秒 Demo 影片（影片頁面另外處理）

```
Generate a 16:9 widescreen pitch deck slide. Dark cyberpunk terminal aesthetic. Black background (#0a0a0a), neon green (#ccff00) accents, white monospace text.

LAYOUT:
- Top left: Small neon green section label "[Live Demonstration]"
- Below section label: White bold title: "Every trade, every signal, every dollar — visible on-chain in real-time"
- CENTER: A 2x2 grid of four dashboard panel mockups, each as a dark card with neon green border:
  TOP-LEFT: "VAULT STATUS" panel — TVL: $47,230 USDC, Shares: 47,230 PALPHA, APY: 18.7%
  TOP-RIGHT: "AI SIGNALS" panel — Last signal: STRONG_BUY (BTC/USDT momentum), Confidence: 87%, Swarm: 4/5 consensus
  BOTTOM-LEFT: "TRADE HISTORY" panel — Table with 3 rows of recent trades: date, market, direction, PnL
  BOTTOM-RIGHT: "SWARM PANEL" panel — 5 persona cards: ContrarianCarl (SELL), TrendFollowerTina (BUY), MomentumMike (BUY), RiskAverseRita (HOLD), DataDrivenDave (BUY). Consensus bar showing 60% BUY
- BOTTOM: Full-width dark bar with neon green text: "🌐 LIVE: polyalpha-dashboard.vercel.app" and white text: "Open now on your phone — scan the QR code on the final slide"
Style: Dashboard screenshot aesthetic. Four panels are equally sized. Swarm Panel is the most visually interesting.
```

---

### SLIDE 8 — Technical Architecture（技術架構）

**修改摘要**：頂部新增 section 標題標籤 `[Technical Architecture]`，原標題保留。

```
Generate a 16:9 widescreen pitch deck slide. Dark cyberpunk terminal aesthetic. Black background (#0a0a0a), neon green (#ccff00) accents, white monospace text.

LAYOUT:
- Top left: Small neon green section label "[Technical Architecture]"
- Below section label: White bold title: "6 smart contracts, 3 system layers — fully modular and auditable"
- LEFT SIDE (50%): A contract table:
  Title: "Smart Contracts (Solidity 0.8.25 · Cancun EVM)"
  Table with columns: Contract | Function | Standard
  PolyAlphaVault.sol | Asset management | ERC-4626
  PALPHAToken.sol | Governance token | ERC-20
  PALPHABuybackBurn.sol | Deflationary burn | Custom
  PALPHAGovernance.sol | DAO voting | OpenZeppelin
  PALPHAStaking.sol | Yield distribution | Custom
  PALPHAOracle.sol | Price feeds | Chainlink-compatible
  Table style: Dark rows, neon green header, monospace font
- RIGHT SIDE (50%): A 3-layer system architecture diagram (vertical):
  TOP LAYER (neon green border): "FRONTEND LAYER — React + TailwindCSS + Vercel"
  MIDDLE LAYER (blue-green border): "OFF-CHAIN AGENT LAYER — Python · GLM-4 · MiroFish · Zep Memory"
  BOTTOM LAYER (neon green border): "ON-CHAIN LAYER — Polygon Amoy Testnet · OpenZeppelin v5"
  Bidirectional arrows between layers
  Below diagram: "chainId: 80002 · Solidity 0.8.25 · evmVersion: cancun"
- BOTTOM: Dark bar: "All contracts verified on-chain. Source code: github.com/YongWilliam-ai/polyalpha-protocol"
Style: Technical reference slide. Table on left, architecture diagram on right.
```

---

### SLIDE 9 — Security Model（安全模型）

**修改摘要**：
1. 頂部新增 section 標題標籤 `[Security Model]`
2. Daily Cap 從 "5 trades/day" 改為 "20 trades/day"
3. 單筆上限從固定 "$500" 改為動態 "0.05% TVL per trade"

```
Generate a 16:9 widescreen pitch deck slide. Dark cyberpunk terminal aesthetic. Black background (#0a0a0a), neon green (#ccff00) accents, white monospace text.

LAYOUT:
- Top left: Small neon green section label "[Security Model]"
- Below section label: White bold title: "6-layer BitPilot Safety Chain — hardcoded in smart contract, impossible to override"
- CENTER: Six hexagonal nodes arranged in a 2x3 grid, each with a dark background and neon green border:
  HEX 01: "🚫 BLACKLIST CHECK — Block dangerous/illiquid markets"
  HEX 02: "📊 POSITION LIMIT — Max 10% TVL per single trade"
  HEX 03: "📅 DAILY CAP — Max 20 trades/day (dynamic)"
  HEX 04: "💵 SIZE LIMIT — Max 0.05% TVL per trade (dynamic, scales with TVL)"
  HEX 05: "🔄 CONFLICT CHECK — No opposing positions in same market"
  HEX 06: "⚡ CIRCUIT BREAKER — Halt ALL trading if drawdown > 20%"
  Connecting arrows between hexagons showing sequential flow
  HEX 06 has a red glow effect to emphasize it as the final safety net
- BOTTOM: Full-width dark red warning bar: "⚠️ CIRCUIT BREAKER: max_drawdown_bps = 2000 (20%) is hardcoded in PolyAlphaVault.sol — no admin override possible"
Style: Six hexagons in a grid. Circuit Breaker hex has red glow. Warning bar at bottom.
```

---

### SLIDE 10 — Tokenomics（代幣經濟學）

**修改摘要**：頂部新增 section 標題標籤 `[Tokenomics]`，原標題保留。

```
Generate a 16:9 widescreen pitch deck slide. Dark cyberpunk terminal aesthetic. Black background (#0a0a0a), neon green (#ccff00) accents, white monospace text.

LAYOUT:
- Top left: Small neon green section label "[Tokenomics]"
- Below section label: White bold title: "PALPHA token aligns all stakeholders through a deflationary buyback-and-burn cycle"
- LEFT SIDE (55%): A large pentagon-shaped cycle flow diagram with 5 nodes:
  NODE 1 (top): "💰 Trading Profits Generated"
  NODE 2 (top-right): "📊 20% Performance Fee Collected"
  NODE 3 (bottom-right): "🔥 10% → Buyback & Burn PALPHA"
  NODE 4 (bottom-left): "📉 PALPHA Supply Decreases"
  NODE 5 (top-left): "📈 PALPHA Value Increases → More Deposits"
  Circular arrows connecting all 5 nodes clockwise in neon green
  Center of pentagon: "PALPHA" in large neon green text + "Deflationary" in white small text
- RIGHT SIDE (45%): Three stacked data cards:
  CARD 1: "Total Supply: 100,000,000 PALPHA"
  CARD 2: "Governance: Vote on strategy parameters"
  CARD 3: "Staking: Earn 50% of management fees"
  Below cards: A simple supply curve chart showing decreasing supply over time with neon green line
- BOTTOM: Dark bar: "10% of all performance fees → automatic buyback-and-burn via PALPHABuybackBurn.sol"
Style: Pentagon cycle diagram is the hero. Clean data cards on the right.
```

---

### SLIDE 11 — Open-Source Integration（開源整合）

**修改摘要**：頂部新增 section 標題標籤 `[Open-Source Integration]`，原標題保留。

```
Generate a 16:9 widescreen pitch deck slide. Dark cyberpunk terminal aesthetic. Black background (#0a0a0a), neon green (#ccff00) accents, white monospace text.

LAYOUT:
- Top left: Small neon green section label "[Open-Source Integration]"
- Below section label: White bold title: "6 proven open-source projects integrated — 10x faster development, institutional-grade quality"
- CENTER: A 2x3 grid of six project cards, each as a dark card with neon green top border:
  CARD 1: "🐟 MiroFish" / "Multi-Agent Swarm AI" / "5 AI personas vote on market signals" / Badge: [CAMEL-AI · Zep Memory]
  CARD 2: "🛡️ BitPilot (bgtask)" / "Safety Chain" / "6-step trade validation, Kelly sizing, daily caps" / Badge: [TypeScript → Python]
  CARD 3: "📊 Polymarket Toolkit" / "CLOB API Client" / "Real-time order book with exponential backoff retry" / Badge: [REST API · Python]
  CARD 4: "📰 6551Team Daily News" / "Sentiment Analysis" / "Real-time news scoring: Bullish/Bearish/Neutral" / Badge: [NLP · REST API]
  CARD 5: "📈 Polymarket CLI" / "PnL Calculator" / "Cash-flow based P&L: Payout - Cost model" / Badge: [Accurate · No Slippage Ignore]
  CARD 6: "📚 Microsoft Qlib" / "Quant Framework" / "Backtesting infrastructure, alpha factor research" / Badge: [Research Only]
- BOTTOM: Dark bar with white text: "All integrations are real code — no mocks, no stubs. Verified in agent/ directory."
Style: 2x3 card grid. Each card has a project icon, name, description, and tech badge.
```

---

### SLIDE 12 — Competitive Landscape（競爭格局）

**修改摘要**：
1. 頂部新增 section 標題標籤 `[Competitive Landscape]`
2. 完善競爭對比表格，5 個核心維度，明確標示 PolyAlpha 是唯一全部具備的平台
3. 底部放大 KEY INSIGHT 結論

```
Generate a 16:9 widescreen pitch deck slide. Dark cyberpunk terminal aesthetic. Black background (#0a0a0a), neon green (#ccff00) accents, white monospace text.

LAYOUT:
- Top left: Small neon green section label "[Competitive Landscape]"
- Below section label: White bold title: "PolyAlpha is the ONLY platform combining all 5 critical features — no direct competitor exists"
- CENTER: A large comparison table:
  Column headers: Feature | PolyAlpha | EdgeBuild | Augur | Polymarket Native | Traditional Quant Fund
  Row 1: On-Chain Transparency | ✅ | ❌ | ✅ | ❌ | ❌
  Row 2: AI Automation | ✅ | ✅ | ❌ | ❌ | ✅
  Row 3: DAO Governance | ✅ | ❌ | ✅ | ❌ | ❌
  Row 4: Open-Source | ✅ | ❌ | ✅ | ❌ | ❌
  Row 5: Non-Custodial | ✅ | ❌ | ✅ | ✅ | ❌
  Row 6: Min Deposit | $10 | $500+ | $100+ | $1 | $1,000,000+
  Row 7: Prediction Market Native | ✅ | ❌ | ✅ | ✅ | ❌
  The PolyAlpha column has ALL green checkmarks and is highlighted with a neon green column background
  Other columns have a mix of ✅ and ❌
  Table style: Dark rows, neon green PolyAlpha column, alternating row shading
- BOTTOM: A large dark card with neon green border spanning full width:
  "🔑 KEY INSIGHT: EdgeBuild is our closest competitor — they have AI automation but lack on-chain transparency, DAO governance, and open-source architecture. We beat them on every dimension that matters for Web3 trust."
Style: Table is the hero. KEY INSIGHT card at the bottom is prominent with neon green border.
```

---

### SLIDE 13 — Strategy Validation（策略驗證）

**修改摘要**：
1. 頂部新增 section 標題標籤 `[Strategy Validation]`
2. Paper Trading Simulation 橫坐標時間線全部 +1 年：2023→2024, 2024→2025, 2025→2026

```
Generate a 16:9 widescreen pitch deck slide. Dark cyberpunk terminal aesthetic. Black background (#0a0a0a), neon green (#ccff00) accents, white monospace text.

LAYOUT:
- Top left: Small neon green section label "[Strategy Validation]"
- Below section label: White bold title: "2-year paper trading simulation confirms the edge: 62.3% win rate, 2.1 Sharpe ratio"
- LEFT SIDE (60%): A line chart titled "Paper Trading Simulation — Cumulative PnL":
  X-axis: Time from Jan 2024 to Dec 2026 (labeled: Jan 2024, Jul 2024, Jan 2025, Jul 2025, Jan 2026, Dec 2026)
  Y-axis: Cumulative PnL in USD ($0 to $35,000)
  Main line: Neon green upward-trending line with some volatility
  Starting point: $0 at Jan 2024
  Ending point: ~$31,400 at Dec 2026 (labeled "+$31,400")
  A gray horizontal baseline at $0
  A red dashed line showing maximum drawdown period (labeled "Max DD: -11.2%")
  Chart background: Dark with subtle grid lines
- RIGHT SIDE (40%): Six performance metric cards in a 2x3 grid:
  Card 1: "62.3%" (neon green large) / "Win Rate" (white)
  Card 2: "2.1" (neon green large) / "Sharpe Ratio" (white)
  Card 3: "11.2%" (yellow large) / "Max Drawdown" (white)
  Card 4: "247" (neon green large) / "Total Trades" (white)
  Card 5: "+$31,400" (neon green large) / "Simulated PnL" (white)
  Card 6: "18.7%" (neon green large) / "Annual Return" (white)
- BOTTOM: Dark bar: "Simulation period: Jan 2024 – Dec 2026 · Cash-flow PnL model (Payout - Cost) · No survivorship bias"
Style: Line chart is the hero. Six metric cards on the right. Time axis updated to 2024-2026.
```

---

### SLIDE 14 — Business Model（商業模式）

**修改摘要**：頂部新增 section 標題標籤 `[Business Model]`，原標題保留。循環流程圖保持原設計。

```
Generate a 16:9 widescreen pitch deck slide. Dark cyberpunk terminal aesthetic. Black background (#0a0a0a), neon green (#ccff00) accents, white monospace text.

LAYOUT:
- Top left: Small neon green section label "[Business Model]"
- Below section label: White bold title: "2/20 hedge fund structure — aligned incentives, sustainable revenue from day one"
- LEFT SIDE (60%): A large circular cycle flow diagram with 5 nodes arranged in a circle:
  NODE 1 (top, neon green): "💰 Investor Deposits USDC" 
  NODE 2 (right): "🏦 Vault Generates Yield"
  NODE 3 (bottom-right): "📊 2% Mgmt Fee + 20% Perf Fee"
  NODE 4 (bottom-left): "🔥 10% → Buyback & Burn PALPHA"
  NODE 5 (left): "📈 PALPHA Value ↑ → More Deposits"
  Circular arrows connecting all nodes clockwise in neon green
  Center of circle: Large "2%" in neon green + "/" + Large "20%" in white
  Below center: "Management / Performance" in small gray text
- RIGHT SIDE (40%): Revenue projection panel:
  Title: "REVENUE PROJECTION" in neon green
  Three scenario bars:
  Scenario 1 (small gray bar): TVL $1M → $57.4K/year ($20K mgmt + $37.4K perf)
  Scenario 2 (medium gray bar): TVL $5M → $287K/year
  Scenario 3 (full neon green bar): TVL $10M → $574K/year [PHASE 3 TARGET]
  Formula box below: "Revenue = (TVL × 2%) + (Annual Profit × 20%)" / "Assuming 18.7% annual return"
- BOTTOM: Dark bar: "High-Water Mark applies to performance fee — only charged when NAV exceeds previous peak"
Style: Circular flow diagram is the hero. Revenue projection panel on the right. Professional hedge fund aesthetic.
```

---

### SLIDE 15 — Roadmap（發展路線）

**修改摘要**：頂部新增 section 標題標籤 `[Roadmap]`，原標題保留。

```
Generate a 16:9 widescreen pitch deck slide. Dark cyberpunk terminal aesthetic. Black background (#0a0a0a), neon green (#ccff00) accents, white monospace text.

LAYOUT:
- Top left: Small neon green section label "[Roadmap]"
- Below section label: White bold title: "From testnet to mainnet in 3 phases — each with a clear, measurable milestone"
- CENTER: Three large phase blocks in a horizontal row connected by thick arrows:
  PHASE 01 (LEFT, neon green border, glowing — CURRENT):
  Badge: "PHASE 01 [ CURRENT ]" in neon green
  Title: "Paper Trading & Validation"
  Checklist (all ✅):
  ✅ 6 smart contracts deployed on testnet
  ✅ 4 AI strategies running in paper mode
  ✅ Backtest: 62.3% win rate validated
  ✅ React dashboard live on Vercel
  ✅ 6 open-source integrations complete
  Timeline: "Q1-Q2 2026"
  ARROW → thick neon green
  PHASE 02 (CENTER, yellow border — NEXT):
  Badge: "PHASE 02 [ NEXT ]" in yellow
  Title: "Testnet Polish & Public Beta"
  List (⏳):
  ⏳ EdgeBuild UI full upgrade
  ⏳ MiroFish swarm live integration
  ⏳ Public beta on testnet
  ⏳ Security audit
  ⏳ DAO governance activation
  Timeline: "Q3 2026"
  ARROW → thick gray
  PHASE 03 (RIGHT, gray border — FUTURE):
  Badge: "PHASE 03 [ FUTURE ]" in gray
  Title: "Mainnet & Live Capital"
  List (🔮):
  🔮 Polygon Mainnet deployment
  🔮 Live capital execution
  🔮 $10M TVL target
  🔮 Full DAO governance
  🔮 Institutional partnerships
  Timeline: "Q4 2026"
- BOTTOM: Full-width progress bar: "CONCEPT ←—[▓▓▓▓▓▓▓▓░░░░░░░░░░░░]→ MAINNET" with "YOU ARE HERE ▼" above the ~35% mark
Style: Three-column phase blocks. Progress bar at bottom. Phase 01 glows to show current status.
```

---

### SLIDE 16 — Conclusion（結語）

**修改摘要**：頂部新增 section 標題標籤 `[Conclusion]`，原標題保留。

```
Generate a 16:9 widescreen pitch deck slide. Dark cyberpunk terminal aesthetic. Black background (#0a0a0a), neon green (#ccff00) accents, white monospace text. This is the FINAL slide — make it impactful and memorable.

LAYOUT:
- Top left: Small neon green section label "[Conclusion]"
- Below section label: White bold title: "PolyAlpha Protocol: from concept to fully functional Web3 + AI protocol in 4 weeks"
- CENTER: Four large achievement stat cards in a 2x2 grid, each as a dark card with neon green glow:
  CARD 1 (top-left): Large "6" in neon green / "Smart Contracts" / "Deployed on Polygon Amoy Testnet" / ⛓ icon
  CARD 2 (top-right): Large "4" in neon green / "AI Strategies" / "Running concurrently in paper mode" / 🤖 icon
  CARD 3 (bottom-left): Large "6" in neon green / "Open-Source Projects" / "Integrated & adapted for production" / 🔗 icon
  CARD 4 (bottom-right): Large "1" in neon green / "Live Dashboard" / "Deployed on Vercel, accessible now" / 🌐 icon
- BOTTOM SECTION: A dark terminal-style box with neon green border spanning full width:
  Left side:
  "root@polyalpha:~$ cat links.txt"
  "> GITHUB:   github.com/YongWilliam-ai/polyalpha-protocol"
  "> DEMO:     polyalpha-dashboard.vercel.app"
  "> CONTACT:  William · ISOM3270 Final Project · HKUST · 2026"
  Right side: A QR code pattern (dark square with QR grid pattern) labeled "Scan for Live Demo"
- Very bottom: Thin neon green line + small gray text: "Built with Claude Code · Deployed with Vercel · Secured by OpenZeppelin v5"
Style: Achievement-focused final slide. Big numbers, terminal CTA box, QR code. Impactful closing.
```

---

## 修改摘要總表

| 頁面 | 修改類型 | 主要變更 |
|---|---|---|
| **新增 Slide 1.5** | 全新頁面 | Agenda 頁，列出 15 個議題 |
| Slide 1 | 小修 | 年份 2025→2026，移除手寫標記 |
| Slide 2 | 中修 | 新增 [Problem Definition] 標籤，加數據來源引用，更新數據至 2025 |
| Slide 3 | 大修 | 新增 [Market Opportunity] 標籤，Bar chart 時間軸更新，2025=$63.5B 實際數據 |
| Slide 4 | 小修 | 新增 [Solution Overview] 標籤 |
| Slide 5 | 大修 | 新增 [How It Works] 標籤，新增 Quarter-Kelly 說明，新增 vs 傳統對沖基金對比表 |
| Slide 6 | 中修 | 新增 [Alpha Engine Mechanism] 標籤，圖表最低點加 BUY、最高點加 SELL |
| Slide 7 | 小修 | 新增 [Live Demonstration] 標籤 |
| Slide 8 | 小修 | 新增 [Technical Architecture] 標籤 |
| Slide 9 | 中修 | 新增 [Security Model] 標籤，Daily Cap 5→20，單筆上限改為動態 0.05% TVL |
| Slide 10 | 小修 | 新增 [Tokenomics] 標籤 |
| Slide 11 | 小修 | 新增 [Open-Source Integration] 標籤 |
| Slide 12 | 大修 | 新增 [Competitive Landscape] 標籤，完善 7 維度比較表，放大 KEY INSIGHT |
| Slide 13 | 中修 | 新增 [Strategy Validation] 標籤，時間軸 +1 年（2024-2026） |
| Slide 14 | 小修 | 新增 [Business Model] 標籤 |
| Slide 15 | 小修 | 新增 [Roadmap] 標籤 |
| Slide 16 | 小修 | 新增 [Conclusion] 標籤 |

**總計：17 頁（原 16 頁 + 新增 Agenda 頁）**
