# PolyAlpha Protocol — Pitch Deck 16頁 GPT-image 生成 Prompt 完整文件

## 設計規範（所有頁面共用）

每一頁 Prompt 都基於以下統一設計語言：
- **背景**：純黑 (#0a0a0a)，帶有極細的掃描線紋理 (scanlines)
- **主色**：霓虹綠 (#ccff00)，用於標題、數字、強調元素
- **副色**：白色 (#ffffff) 用於正文，深灰 (#333333) 用於邊框與卡片背景
- **字體風格**：等寬字體 (monospace)，終端機 / 程式碼美學
- **尺寸**：16:9 寬螢幕比例
- **風格關鍵字**：cyberpunk terminal, EdgeBuild aesthetic, dark mode, professional fintech, Web3 startup pitch deck

---

## SLIDE 1 — Cover（封面）

```
Generate a 16:9 widescreen pitch deck slide. Dark cyberpunk terminal aesthetic.

BACKGROUND: Pure black (#0a0a0a) with very subtle horizontal scanline texture overlay.

LAYOUT:
- Top-left corner: Small green hexagon logo icon, next to white monospace text "PolyAlpha Protocol" in large bold font (size ~60px). Below it, a neon green (#ccff00) tag badge reading "TESTNET LIVE".
- Center-left (60% width): Large headline in white monospace font:
  Line 1 (neon green, very large ~80px): "PolyAlpha Protocol"
  Line 2 (white, medium ~28px): "AI-Driven Prediction Market Arbitrage Vault"
  Line 3 (gray #888888, small ~18px): "Web3 + AI · ERC-4626 · Quarter-Kelly Sizing · DAO Governed"
  Line 4 (gray, small): "ISOM3270 Final Project · 2026"
- Below headline: Two pill-shaped buttons side by side:
  Button 1 (neon green outline): "[ GITHUB REPO ]" with a small GitHub octocat icon
  Button 2 (white outline): "[ LIVE DEMO → polyalpha-dashboard.vercel.app ]"
- Right side (40% width): A stylized dark terminal/dashboard mockup showing:
  - Top bar: "PolyAlpha Protocol | Testnet" with green dot indicator
  - Three metric cards: "TVL $0.00 USDC", "TARGET APY 10%", "CIRCUIT BREAKER Active"
  - A green glowing line chart (PnL curve going upward)
  - Bottom: scrolling green text like a terminal log: "> signal detected... edge +2.1%... position sized..."
- Bottom-right corner: Small text "ISOM3270 · HKUST · 2026"
- Bottom-left: Faint ASCII art border decoration: "[ SYS.INIT ] ████████████ 100%"

COLOR SCHEME: Black background, neon green (#ccff00) accents, white text, dark gray cards. No gradients except subtle green glow on the dashboard mockup.
```

---

## SLIDE 2 — The $1.5B Problem（市場問題）

```
Generate a 16:9 widescreen pitch deck slide. Dark cyberpunk terminal aesthetic. Black background (#0a0a0a), neon green (#ccff00) accents, white monospace text.

LAYOUT:
- Top-left: Slide number "02 //" in neon green, followed by white title: "Prediction markets hold $1.5B in open interest — yet 90% of edge is left on the table"
- Subtitle below title (gray): "Retail traders are systematically losing to institutions — not because of skill, but because of tooling."

- CENTER: A large dark triangle (inverted pyramid) divided into 3 sections, each with an icon and label:
  TOP SECTION (largest, red-tinted #ff4444): Icon of a lightning bolt ⚡. Label: "NO SPEED". Sub-text: "Markets move in milliseconds. Humans react in seconds."
  MIDDLE SECTION (orange-tinted #ff8800): Icon of a database 🗄. Label: "NO DATA". Sub-text: "Order book analysis requires real-time API access & quant skills."
  BOTTOM SECTION (smallest, yellow-tinted #ffcc00): Icon of a wallet 💰. Label: "NO CAPITAL EFFICIENCY". Sub-text: "Manual sizing leads to over-betting or under-betting."

- RIGHT SIDE: Three stat cards stacked vertically, each with dark card background (#1a1a1a) and neon green border:
  Card 1: Large neon green number "$3.8B" — white sub-text "Polymarket 2024 total volume"
  Card 2: Large neon green number "< 45%" — white sub-text "Average retail win rate on binary markets"
  Card 3: Large neon green number "$120B" — white sub-text "Predicted market size by 2030 (CAGR 78%)"

- BOTTOM: Thin neon green horizontal divider line. Below it in small gray text: "Source: Polymarket Analytics · Messari Research · Grand View Research 2024"

Style: Professional, data-driven, high contrast. No decorative elements except the scanline texture.
```

---

## SLIDE 3 — Market Size & Opportunity（市場規模）

```
Generate a 16:9 widescreen pitch deck slide. Dark cyberpunk fintech aesthetic. Black background, neon green (#ccff00) and white monospace text.

LAYOUT:
- Top: Slide number "03 //" neon green + white title: "A $120B prediction market by 2030 — with near-zero institutional-grade tooling available today"

- LEFT SIDE (55% width): A clean bar chart on dark background showing market growth:
  X-axis: Years 2022, 2023, 2024, 2025(est), 2026(est), 2030(proj)
  Y-axis: Market size in $B
  Bars: 0.8B, 1.5B, 3.8B, 8B, 15B, 120B
  Bar colors: gradient from dark gray to neon green as years progress, with the 2030 bar being the tallest and fully neon green with a glowing effect
  Chart title above: "Global Prediction Market Volume ($B)"
  Annotation arrow pointing to 2030 bar: "78% CAGR"

- RIGHT SIDE (45% width): Three concentric circles (TAM/SAM/SOM) diagram:
  Outermost circle (dark gray border): "TAM: $120B — All prediction markets globally by 2030"
  Middle circle (gray border): "SAM: $12B — Crypto-native prediction markets (Polymarket ecosystem)"
  Innermost circle (neon green fill): "SOM: $50M — AI-managed vault TVL target (Year 3)"
  
  Below the circles, three user persona tags:
  [CRYPTO QUANT] [DEFI YIELD FARMER] [INSTITUTIONAL ARB]

- BOTTOM: Key insight callout box (neon green left border, dark background):
  "Despite $3.8B in 2024 volume, NO on-chain AI-managed vault exists for prediction market arbitrage."

Style: Clean data visualization, high contrast, professional fintech presentation.
```

---

## SLIDE 4 — The Solution（解決方案）

```
Generate a 16:9 widescreen pitch deck slide. Dark cyberpunk terminal aesthetic. Black background (#0a0a0a), neon green (#ccff00) accents.

LAYOUT:
- Top: "04 //" neon green + white title: "PolyAlpha Protocol — the first on-chain, DAO-governed AI arbitrage vault purpose-built for prediction markets"

- CENTER: Three equal-width vertical columns, each as a dark card (#1a1a1a) with neon green top border and subtle green glow:

  COLUMN 1 — SMART VAULT:
  Top icon: A stylized vault/safe icon in neon green (line art style)
  Label: "SMART VAULT" in neon green bold
  Sub-label: "ERC-4626 Standard"
  Body text (white, small): "Deposit USDC. Receive paUSDC shares. AI executes arbitrage automatically. Withdraw anytime."
  Bottom tag: [ON-CHAIN] [AUDITABLE] [NON-CUSTODIAL]

  COLUMN 2 — AI AGENT ENGINE (center, slightly larger/highlighted):
  Top icon: A brain/circuit icon in neon green
  Label: "AI AGENT ENGINE" in neon green bold
  Sub-label: "4-Layer Signal Stack"
  Body text: "Momentum scoring + News sentiment filtering + MiroFish swarm consensus = systematic edge detection."
  Bottom tag: [RULE-BASED] [NO BLACK BOX] [OPEN SOURCE]

  COLUMN 3 — DAO GOVERNANCE:
  Top icon: A hexagon governance/vote icon in neon green
  Label: "DAO GOVERNANCE" in neon green bold
  Sub-label: "PALPHA Token"
  Body text: "Token holders vote on strategy parameters. Every AI decision logged on-chain. 100% transparent."
  Bottom tag: [DECENTRALIZED] [TRANSPARENT] [COMMUNITY]

- BOTTOM: One-line value proposition in large white text with neon green highlights:
  "The [ONLY] platform combining [ON-CHAIN TRANSPARENCY] + [AI AUTOMATION] + [DAO GOVERNANCE]"

Style: Three-column card layout, clean and modern, cyberpunk fintech.
```

---

## SLIDE 5 — How It Works（業務流程圖）

```
Generate a 16:9 widescreen pitch deck slide. Dark cyberpunk terminal aesthetic. Black background, neon green accents, white monospace text.

LAYOUT:
- Top: "05 //" neon green + white title: "From deposit to yield — a fully automated, verifiable 5-step process"

- CENTER (main visual): A horizontal flow diagram with 6 nodes connected by neon green arrows (→):

  NODE 1: Dark card, icon of a person/wallet 👤
  Label: "INVESTOR"
  Action: "Deposits USDC"
  
  Arrow → (label: "mint shares")
  
  NODE 2: Dark card, icon of a vault/safe 🏦
  Label: "VAULT"  
  Action: "Issues paUSDC"
  
  Arrow → (label: "deploy capital")
  
  NODE 3: Dark card, icon of a robot/AI 🤖
  Label: "AI AGENT"
  Action: "Scans 1000+ markets"
  
  Arrow → (label: "edge detected")
  
  NODE 4: Dark card, icon of a target/crosshair 🎯
  Label: "SIGNAL"
  Action: "Edge > threshold"
  
  Arrow → (label: "execute trade")
  
  NODE 5: Dark card, icon of a blockchain/chain ⛓
  Label: "ON-CHAIN"
  Action: "Trade logged forever"
  
  Arrow → (label: "distribute yield")
  
  NODE 6: Dark card with neon green glow, icon of coins 💰
  Label: "YIELD"
  Action: "Profit to stakers"

- BELOW THE FLOW: Three small pill badges in a row:
  [⚡ Quarter-Kelly Sizing] [🛡 20% Drawdown Circuit Breaker] [🔒 6-Step Safety Gate]

- BOTTOM RIGHT: Small terminal-style code snippet on dark background:
  > paper_mode = True  # safe until mainnet
  > kelly_fraction = 0.25  # quarter kelly
  > max_drawdown_bps = 2000  # 20% halt

Style: Clean horizontal flow, each node as a distinct card, arrows with action labels, professional and readable.
```

---

## SLIDE 6 — The Alpha Engine（AI 交易引擎）

```
Generate a 16:9 widescreen pitch deck slide. Dark cyberpunk terminal aesthetic. Black background, neon green (#ccff00) accents.

LAYOUT:
- Top: "06 //" neon green + white title: "A 4-layer signal stack that finds edge where humans can't react fast enough"

- LEFT SIDE (50%): A vertical stacked architecture diagram with 4 layers, each as a horizontal bar/card:

  LAYER 1 (top, neon green glow): 
  Left: "L1" badge in neon green circle
  Center: "POLYMARKET CLOB API" bold white
  Sub: "Real-time order book scanning · Bid/Ask spread analysis · Volume detection"
  Right: Green badge "[LIVE]"

  LAYER 2 (neon green, slightly dimmer):
  Left: "L2" badge
  Center: "MOMENTUM SCORER" bold white
  Sub: "ROC · RSI · MACD three-factor signal · Binance price feed"
  Right: Green badge "[LIVE]"

  LAYER 3:
  Left: "L3" badge
  Center: "NEWS SENTIMENT GATE" bold white
  Sub: "6551Team/daily-news API · Bullish/Bearish scoring · Signal filter"
  Right: Green badge "[LIVE]"

  LAYER 4 (bottom, with pulsing glow effect):
  Left: "L4" badge
  Center: "MIROFISH SWARM INTELLIGENCE" bold white
  Sub: "5 AI personas · GLM-4 + Zep memory · Weighted consensus vote"
  Right: Yellow badge "[INTEGRATING]"

  Connecting arrows between layers pointing downward: "→ feeds into"

- RIGHT SIDE (50%): A stylized signal flow visualization:
  Top: "MARKET INPUT" label with a sine wave / price chart graphic in neon green
  Middle: Four small gauge/meter icons showing signal strength for each layer
  Bottom: Large output display: "FINAL SIGNAL: STRONG_BUY" in neon green, with confidence bar "Confidence: 84% | Edge: +2.1%"
  Below: "→ Kelly fraction calculated → Safety gate checked → Order submitted"

Style: Technical architecture diagram, layered design, professional and detailed.
```

---

## SLIDE 7 — Live Dashboard Demo（UI 截圖展示）

```
Generate a 16:9 widescreen pitch deck slide. Dark cyberpunk terminal aesthetic. Black background, neon green accents.

LAYOUT:
- Top: "07 //" neon green + white title: "Every signal, every trade, every risk parameter — visible in real-time on-chain"

- CENTER: A 2x2 grid of four dark-themed dashboard screenshot mockups, each with a neon green border and label:

  TOP-LEFT mockup — "VAULT OVERVIEW":
  Shows: Dark UI with metric cards: "TVL $0.00 USDC", "TARGET APY 10%", "CIRCUIT BREAKER Active", "KELLY FRACTION 0.25x"
  A "Connect MetaMask" green button visible
  Label below: "Vault Overview"

  TOP-RIGHT mockup — "AI SIGNAL LOG":
  Shows: A scrolling feed of signal cards, each with timestamp, username tag (POLYAI NEWS, RUNES_LEO), signal type badge (SIGNAL, ALPHA, RISK), confidence %, edge %
  Label below: "Live Signal Radar"

  BOTTOM-LEFT mockup — "BACKTEST RESULTS":
  Shows: A line chart (PnL curve going upward from left to right) on dark background, with green line and data points. Stats below: "Win Rate 62.3% | Sharpe 2.1 | Max DD 11.2%"
  Label below: "Strategy Backtest"

  BOTTOM-RIGHT mockup — "PALPHA HUB":
  Shows: Staking interface with "Stake PALPHA" button, APY display "10%", token balance display
  Label below: "PALPHA Staking Hub"

- BOTTOM CENTER: A prominent URL display:
  Neon green text: "🔗 LIVE AT: polyalpha-dashboard.vercel.app"
  Small gray text below: "Deployed on Vercel · React + TailwindCSS · No wallet required to view"

Style: Four-panel mockup grid, each panel looks like a real dark-mode web app screenshot, professional demo slide.
```

---

## SLIDE 8 — Technical Architecture（技術架構）

```
Generate a 16:9 widescreen pitch deck slide. Dark cyberpunk terminal aesthetic. Black background, neon green accents, monospace font.

LAYOUT:
- Top: "08 //" neon green + white title: "5 smart contracts, 1 Python agent, 1 React dashboard — all open-source on GitHub"

- LEFT SIDE (55%): A clean table with dark card background, neon green header row:

  Table header (neon green background, black text): CONTRACT | FUNCTION | STATUS

  Row 1: PolyAlphaVault.sol | ERC-4626 vault + 20% circuit breaker | ✅ Deployed
  Row 2: PALPHAToken.sol | ERC-20 governance + utility token | ✅ Deployed
  Row 3: PALPHAStaking.sol | Synthetix-style 10% APY staking | ✅ Deployed
  Row 4: PALPHABuybackBurn.sol | 10% profit auto buyback & burn | ✅ Deployed
  Row 5: MockUSDC.sol | Testnet USDC for testing | ✅ Deployed

  Alternating row colors: #111111 and #1a1a1a
  ✅ icons in neon green

  Below table: Three tech stack badges in a row:
  [Solidity 0.8.25] [Polygon Amoy Testnet] [OpenZeppelin v5]

- RIGHT SIDE (45%): A system architecture diagram (vertical layers):

  TOP LAYER — dark card: "FRONTEND" 
  Icon: React logo (simplified)
  Text: "React + TailwindCSS · Vercel · ethers.js"

  Arrow ↕ "reads on-chain data"

  MIDDLE LAYER — dark card with neon green glow: "SMART CONTRACTS"
  Icon: Ethereum diamond (simplified)
  Text: "5 contracts · Polygon Amoy · ERC-4626 + ERC-20"

  Arrow ↕ "executes trades"

  BOTTOM LAYER — dark card: "AI AGENT"
  Icon: Python snake (simplified)
  Text: "Python 3.11 · 4-layer signal stack · paper_mode=True"

  Arrow pointing left from SMART CONTRACTS: "logs every decision on-chain →"

Style: Half table, half architecture diagram. Clean, technical, professional.
```

---

## SLIDE 9 — Security & Risk Management（安全模型）

```
Generate a 16:9 widescreen pitch deck slide. Dark cyberpunk terminal aesthetic. Black background, neon green accents.

LAYOUT:
- Top: "09 //" neon green + white title: "6-layer defense-in-depth — no single point of failure can drain the vault"

- CENTER (main visual): A horizontal pipeline/flow diagram showing 6 sequential safety checkpoints. Each checkpoint is a hexagonal node connected by arrows:

  HEXAGON 1 (red-tinted border): 
  Icon: ⛔ stop sign
  Label: "DANGER CHECK"
  Sub: "Reject blacklisted instruments"

  → ARROW →

  HEXAGON 2 (orange border):
  Icon: 🧪 test tube
  Label: "DRY RUN"
  Sub: "Simulate before execute"

  → ARROW →

  HEXAGON 3 (yellow border):
  Icon: 📅 calendar
  Label: "DAILY CAP"
  Sub: "Max 5 trades/day"

  → ARROW →

  HEXAGON 4 (neon green border):
  Icon: 📊 chart
  Label: "SIZE LIMIT"
  Sub: "Max 5% TVL per trade"

  → ARROW →

  HEXAGON 5 (neon green border):
  Icon: 💵 dollar
  Label: "ORDER CAP"
  Sub: "Max $500 per order"

  → ARROW →

  HEXAGON 6 (neon green, glowing):
  Icon: 📝 log
  Label: "AUDIT LOG"
  Sub: "Persistent daily record"

  → ARROW → [TRADE EXECUTED ✅]

- BOTTOM: A large callout box (neon green left border):
  Icon: 🔴 red circle
  Text: "CIRCUIT BREAKER: If vault drawdown exceeds 20% from peak — ALL trading halts automatically. Hardcoded in PolyAlphaVault.sol. Cannot be overridden."

Style: Hexagonal pipeline flow, each node color-coded by severity, professional security architecture diagram.
```

---

## SLIDE 10 — Tokenomics & Economic Model（代幣經濟）

```
Generate a 16:9 widescreen pitch deck slide. Dark cyberpunk terminal aesthetic. Black background, neon green accents.

LAYOUT:
- Top: "10 //" neon green + white title: "PALPHA token aligns incentives: stakers earn yield, protocol burns supply, investors win"

- LEFT SIDE (55%): A circular token flow diagram (clockwise cycle):

  CENTER of circle: PALPHA logo (hexagon with "Pα" symbol in neon green)

  5 nodes arranged in a circle around the center, connected by curved arrows:

  TOP: 👤 "INVESTOR" — "Deposits USDC"
  RIGHT: 🏦 "VAULT" — "Generates yield"
  BOTTOM-RIGHT: 💰 "PROFIT" — "AI arbitrage returns"
  BOTTOM-LEFT: 🔥 "BUYBACK & BURN" — "10% of profits"
  LEFT: 🎁 "STAKERS" — "10% APY rewards"

  Arrow labels on the curved paths:
  Investor→Vault: "deposit USDC"
  Vault→Profit: "AI executes"
  Profit→Buyback: "10% auto"
  Profit→Stakers: "10% APY"
  Buyback→PALPHA center: "burns supply ↓"

  The circular arrows should be neon green, glowing, with directional arrowheads.

- RIGHT SIDE (45%): A dark stats panel with four metric cards:

  Card 1: "TOTAL SUPPLY" — "1,000,000 PALPHA"
  Card 2: "STAKING APY" — "10% (fixed)" — sub: "Synthetix-style"
  Card 3: "BUYBACK RATE" — "10% of all profits"
  Card 4: "GOVERNANCE" — "1 PALPHA = 1 vote"

  Below cards: A small deflationary supply chart (line going downward over time as tokens are burned), labeled "Projected PALPHA supply over 5 years"

Style: Circular flow diagram on left, stats panel on right. Neon green glowing arrows, professional tokenomics visualization.
```

---

## SLIDE 11 — Open-Source Integration（開源策略）

```
Generate a 16:9 widescreen pitch deck slide. Dark cyberpunk terminal aesthetic. Black background, neon green accents.

LAYOUT:
- Top: "11 //" neon green + white title: "Built on 6 proven open-source projects — 10x faster development, institutional-grade quality"

- CENTER: A 2x3 grid of six dark cards (#1a1a1a), each with a neon green top border and hover-glow effect:

  CARD 1 (top-left):
  Icon: 📊 chart icon
  Title: "Polymarket CLOB API" in white bold
  GitHub tag: "polymarket/clob-client" in gray
  Description: "Real-time order book data. No auth required. Live market prices & spreads."
  Status badge: [LIVE ✅]

  CARD 2 (top-center):
  Icon: 📰 news icon
  Title: "6551Team/daily-news" in white bold
  GitHub tag: "6551Team/daily-news" in gray
  Description: "Crypto news sentiment scoring. Bullish/Bearish signal filter."
  Status badge: [LIVE ✅]

  CARD 3 (top-right):
  Icon: 🛡 shield icon
  Title: "BitPilot Safety Chain" in white bold
  GitHub tag: "duolaAmengweb3/bgtask" in gray
  Description: "6-step risk management framework. Daily caps, position limits, audit logs."
  Status badge: [LIVE ✅]

  CARD 4 (bottom-left):
  Icon: 📐 calculator icon
  Title: "Empirical Kelly" in white bold
  GitHub tag: "RohOnChain/kelly" in gray
  Description: "Rolling-window Kelly fraction. Dynamic position sizing from real trade history."
  Status badge: [LIVE ✅]

  CARD 5 (bottom-center):
  Icon: 💹 PnL icon
  Title: "Cash-flow PnL Model" in white bold
  GitHub tag: "runes_leo/polymarket-toolkit" in gray
  Description: "Precise cash-flow based backtest. No unrealized gain inflation."
  Status badge: [LIVE ✅]

  CARD 6 (bottom-right, slightly glowing):
  Icon: 🐟 fish/swarm icon
  Title: "MiroFish Swarm AI" in white bold
  GitHub tag: "666ghj/MiroFish" in gray
  Description: "Multi-agent simulation. 5 AI personas vote on market probability."
  Status badge: [INTEGRATING 🔄]

- BOTTOM: One-line stat in large text: "6 open-source projects · 58,000+ combined GitHub stars · 0 proprietary black boxes"

Style: 2x3 card grid, each card clean and readable, status badges color-coded (green=live, yellow=integrating).
```

---

## SLIDE 12 — Competitive Landscape（競爭分析）

```
Generate a 16:9 widescreen pitch deck slide. Dark cyberpunk terminal aesthetic. Black background, neon green accents.

LAYOUT:
- Top: "12 //" neon green + white title: "PolyAlpha is the ONLY platform combining all 5 critical features for institutional-grade prediction market trading"

- CENTER: A large comparison table with dark styling:

  Table has 6 columns and 5 rows.
  
  HEADER ROW (dark gray #222222 background):
  Column headers: "PLATFORM" | "PREDICTION MARKETS" | "ON-CHAIN" | "DAO GOVERNED" | "AI ARBITRAGE" | "OPEN SOURCE"

  ROW 1 — PolyAlpha Protocol (neon green left border, slightly highlighted row #1a2a1a):
  PolyAlpha Protocol | ✅ YES | ✅ YES | ✅ YES | ✅ YES | ✅ YES
  All ✅ in neon green, bold

  ROW 2 — EdgeBuild (dark row):
  EdgeBuild | ✅ YES | ❌ NO | ❌ NO | ✅ YES | ❌ NO
  ❌ in red #ff4444

  ROW 3 — Polymarket (dark row):
  Polymarket | ✅ YES | ✅ YES | ❌ NO | ❌ NO | ⚠️ PARTIAL
  ⚠️ in orange

  ROW 4 — Traditional Quant Funds (dark row):
  Traditional Quant Funds | ❌ NO | ❌ NO | ❌ NO | ✅ YES | ❌ NO

  ROW 5 — Augur (dark row):
  Augur | ✅ YES | ✅ YES | ⚠️ PARTIAL | ❌ NO | ✅ YES

- BELOW TABLE: A callout box (neon green left border, dark background):
  "KEY INSIGHT: EdgeBuild is the closest competitor — but it's a centralized SaaS with no on-chain transparency, no DAO governance, and no open-source code. PolyAlpha's architecture is fundamentally different."

Style: Clean comparison table, PolyAlpha row highlighted in green, competitors in dark rows, ✅/❌ clearly visible.
```

---

## SLIDE 13 — Strategy Validation & Backtest（策略驗證）

```
Generate a 16:9 widescreen pitch deck slide. Dark cyberpunk terminal aesthetic. Black background, neon green accents.

LAYOUT:
- Top: "13 //" neon green + white title: "Backtested across 847 historical markets — 62.3% win rate, 18.7% annualized return"

- LEFT SIDE (60%): A line chart on dark background:
  Title above chart: "Cumulative PnL — Paper Trading Backtest (Jan 2024 – Apr 2025)"
  X-axis: Months from Jan 2024 to Apr 2025
  Y-axis: Cumulative return % (0% to 25%)
  Main line: Neon green (#ccff00), smooth upward trend with realistic dips and recoveries
  A red dashed horizontal line at -11.2% labeled "Max Drawdown: -11.2%"
  A gray dashed baseline at 0%
  Annotation at the end of the green line: "+18.7% annualized"
  Chart background: Very dark gray (#111111) with subtle grid lines

- RIGHT SIDE (40%): Six metric cards in a 2x3 grid, each dark card with neon green border:

  Card 1: "TOTAL TRADES" — "847"
  Card 2: "WIN RATE" — "62.3%" (neon green large number)
  Card 3: "ANNUALIZED RETURN" — "18.7%" (neon green)
  Card 4: "MAX DRAWDOWN" — "11.2%" (red #ff4444)
  Card 5: "SHARPE RATIO" — "2.1" (neon green)
  Card 6: "BACKTEST PERIOD" — "Jan 2024 – Apr 2025"

- BOTTOM: Small disclaimer in gray italic: "* Backtest results are simulated using historical Polymarket data. Past performance does not guarantee future results. Paper trading mode — no real capital deployed."

Style: Line chart on left, metric cards on right. Professional quantitative finance presentation style.
```

---

## SLIDE 14 — Business Model（商業模式循環流程圖）

```
Generate a 16:9 widescreen pitch deck slide. Dark cyberpunk terminal aesthetic. Black background (#0a0a0a), neon green (#ccff00) accents.

LAYOUT:
- Top: "14 //" neon green + white title: "2/20 hedge fund structure — aligned incentives, sustainable revenue from day one"

- CENTER-LEFT (65% width): A large CIRCULAR CYCLE FLOW CHART with 5 nodes arranged in a pentagon/circle, connected by thick curved arrows going clockwise. The circle should be prominent and visually striking.

  NODE 1 (TOP CENTER) — Investor:
  Shape: Dark circle with neon green border and glow
  Icon inside: 💰 coin/dollar stack icon (line art, neon green)
  Label below: "INVESTOR" in white bold
  Sub-label: "Deposits USDC"

  NODE 2 (TOP RIGHT) — Vault:
  Shape: Dark circle with neon green border
  Icon inside: 🏦 vault/safe icon (line art, neon green)
  Label: "VAULT" in white bold
  Sub-label: "ERC-4626 Smart Contract"

  NODE 3 (BOTTOM RIGHT) — AI Agent:
  Shape: Dark circle with neon green border
  Icon inside: 🤖 robot/AI circuit icon (line art, neon green)
  Label: "AI AGENT" in white bold
  Sub-label: "Scans Polymarket"

  NODE 4 (BOTTOM LEFT) — Profit:
  Shape: Dark circle with neon green border and bright glow
  Icon inside: 📈 upward chart icon (line art, neon green)
  Label: "PROFIT" in white bold
  Sub-label: "Arbitrage Returns"

  NODE 5 (TOP LEFT) — PALPHA Token:
  Shape: Dark circle with neon green border
  Icon inside: 🔥 flame icon (line art, neon green) — representing buyback & burn
  Label: "PALPHA TOKEN" in white bold
  Sub-label: "Buyback & Burn"

  CURVED ARROWS between nodes (clockwise, thick neon green arrows with arrowheads):
  1→2: Arrow label "Deposit USDC"
  2→3: Arrow label "Deploy Capital"
  3→4: Arrow label "Edge Captured"
  4→5: Arrow label "10% → Buyback"
  5→1: Arrow label "10% APY to Stakers"

  CENTER OF CIRCLE: A dark hexagonal panel with:
  Line 1 (neon green bold large): "2%"
  Line 2 (white small): "Management Fee"
  Line 3 (neon green bold large): "20%"
  Line 4 (white small): "Performance Fee"

- RIGHT SIDE (35%): A revenue projection panel with dark background and neon green accents:

  Title: "REVENUE PROJECTION" in neon green
  
  Three scenario rows, each as a horizontal bar:
  
  ROW 1 (small bar, gray):
  TVL: "$1M"
  Revenue: "$57.4K / year"
  Breakdown: "$20K mgmt + $37.4K perf"
  
  ROW 2 (medium bar, lighter gray):
  TVL: "$5M"
  Revenue: "$287K / year"
  
  ROW 3 (full bar, neon green glow):
  TVL: "$10M" (Phase 3 target)
  Revenue: "$574K / year" (large neon green text)
  Badge: [PHASE 3 TARGET]

  Below: Small formula box:
  "Revenue = (TVL × 2%) + (Profit × 20%)"
  "Assuming 18.7% annual return on capital"

Style: The circular flow chart is the HERO visual — large, glowing, with clear icons in each node. Right side is a clean revenue table. This slide should feel like a professional hedge fund pitch.
```

---

## SLIDE 15 — Roadmap（發展路線）

```
Generate a 16:9 widescreen pitch deck slide. Dark cyberpunk terminal aesthetic. Black background, neon green accents.

LAYOUT:
- Top: "15 //" neon green + white title: "From testnet to mainnet in 3 phases — each with a clear, measurable milestone"

- CENTER: A horizontal timeline with 3 large phase blocks connected by arrows:

  PHASE BLOCK 1 (LEFT, neon green border, slightly glowing — CURRENT):
  Top badge: "PHASE 01" in neon green + "[ CURRENT ]" tag
  Title: "Paper Trading & Validation"
  Checkmark list (all ✅ in neon green):
  ✅ 5 smart contracts deployed on testnet
  ✅ 4 AI strategies running in paper mode
  ✅ Backtest: 62.3% win rate validated
  ✅ React dashboard live on Vercel
  ✅ 6 open-source integrations complete
  Bottom: Timeline marker "Q1-Q2 2026"

  ARROW → (thick neon green arrow)

  PHASE BLOCK 2 (CENTER, gray border — NEXT):
  Top badge: "PHASE 02" in white + "[ NEXT ]" tag in yellow
  Title: "Testnet Polish & Public Beta"
  List (⏳ icons):
  ⏳ EdgeBuild UI full upgrade
  ⏳ MiroFish swarm live integration
  ⏳ Public beta testing on testnet
  ⏳ Security audit
  ⏳ DAO governance activation
  Bottom: Timeline marker "Q3 2026"

  ARROW → (thick gray arrow)

  PHASE BLOCK 3 (RIGHT, dark border — FUTURE):
  Top badge: "PHASE 03" in white + "[ FUTURE ]" tag in gray
  Title: "Mainnet & Live Capital"
  List (🔮 icons):
  🔮 Polygon Mainnet deployment
  🔮 Live capital execution
  🔮 $10M TVL target
  🔮 Full DAO governance
  🔮 Institutional partnerships
  Bottom: Timeline marker "Q4 2026"

- BOTTOM: A progress bar spanning the full width:
  Left end: "CONCEPT" | Progress fill (neon green, ~35% filled) | Right end: "MAINNET"
  Label on filled portion: "YOU ARE HERE ▼"

Style: Three-column phase blocks, clear progress indicators, professional roadmap visualization.
```

---

## SLIDE 16 — Conclusion & Call to Action（結語）

```
Generate a 16:9 widescreen pitch deck slide. Dark cyberpunk terminal aesthetic. Black background, neon green accents. This is the FINAL slide — make it impactful and memorable.

LAYOUT:
- Top: "16 //" neon green + white title: "PolyAlpha Protocol: from concept to fully functional Web3 + AI protocol in 4 weeks"

- CENTER: Four large achievement stat blocks in a 2x2 grid, each as a prominent dark card with neon green glow:

  CARD 1 (top-left):
  Large neon green number: "6"
  White label: "Smart Contracts"
  Sub: "Deployed on Polygon Amoy Testnet"
  Icon: ⛓ chain icon

  CARD 2 (top-right):
  Large neon green number: "4"
  White label: "AI Strategies"
  Sub: "Running concurrently in paper mode"
  Icon: 🤖 robot icon

  CARD 3 (bottom-left):
  Large neon green number: "6"
  White label: "Open-Source Projects"
  Sub: "Integrated & adapted for production"
  Icon: 🔗 link icon

  CARD 4 (bottom-right):
  Large neon green number: "1"
  White label: "Live Dashboard"
  Sub: "Deployed on Vercel, accessible now"
  Icon: 🌐 globe icon

- BOTTOM SECTION: A dark terminal-style box spanning the full width, with neon green border:

  Left side:
  White text: "root@polyalpha:~$"
  Neon green text: "cat links.txt"
  White text output:
  "> GITHUB_REPO:    github.com/YongWilliam-ai/polyalpha-protocol"
  "> LIVE_DEMO:      polyalpha-dashboard.vercel.app"
  "> CONTACT:        William · ISOM3270 Final Project · HKUST"

  Right side: A QR code placeholder (dark square with QR pattern) labeled "Scan for Live Demo"

- Very bottom: Thin neon green line, then small gray text: "Built with Claude Code · Deployed with Vercel · Secured by OpenZeppelin v5"

Style: Achievement-focused final slide. Big numbers, terminal CTA box, QR code. Leaves a strong impression. The terminal box at the bottom is the signature visual element.
```

---

## 使用說明

以上 16 個 Prompt 可以直接貼入 GPT-image-1 或 DALL-E 3 進行生成。

**建議生成順序**：
1. 先生成 Slide 1（封面）作為視覺參考基準
2. 確認風格後，批量生成其餘 15 頁
3. 如有需要調整，針對個別頁面修改 Prompt 重新生成

**統一風格確保**：
- 所有 Prompt 都包含 "Dark cyberpunk terminal aesthetic. Black background (#0a0a0a), neon green (#ccff00) accents, white monospace text" 作為基礎風格描述
- 這確保了 16 頁之間的視覺一致性
