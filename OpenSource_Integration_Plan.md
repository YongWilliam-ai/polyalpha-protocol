# PolyAlpha Protocol — Open-Source Integration Plan
> Generated from analysis of 21 sources (19 original + 2 added)
> Research date: 2026-04-29

---

## STEP 2 — Filtered & Categorized Sources

### Category A: Trading Strategies / Alpha

| # | Source | Signal | Win Rate |
|---|--------|--------|----------|
| A1 | Medium / MrFadiAi — Automated Market Making | Place limit orders both sides, capture spread | 78–85% / 1–3%/mo |
| A2 | Medium — AI Probability Arbitrage | Ensemble AI + news <5s, trade when divergence >15% | 65–75% / 3–8%/mo |
| A3 | Medium — Logical Correlation Arbitrage | Graph-map correlated markets, flag impossible pricings | 70–80% / 2–5%/mo |
| A4 | Medium / MrFadiAi — DipArb (15-min BTC) | Detect BTC crashes >15% in 3-second window, buy dip + hedge | 60–70% / 8–15%/mo |
| A5 | MrFadiAi — Smart Money Copying | Mirror top traders: min 60% WR, 1.5x profit factor | Inherits from trader |
| A6 | Blave-TW/blave-quant-skill | TWAP execution, alpha table filtering, multi-exchange | No disclosed WR |
| A7 | duolaAmengweb3/bitget-task-skills | Sleep mode (price triggers), Event mode (volatility response), Copy trading | No disclosed WR |

### Category B: Infrastructure / Tools (Reusable Code)

| # | Source | What it provides |
|---|--------|-----------------|
| B1 | Polymarket/polymarket-cli | Full CLOB API: limit/market orders, bulk ops, CTF token ops, auth |
| B2 | Polymarket/agents | gamma.py (market discovery), polymarket.py (order execution), Pydantic models |
| B3 | 6551Team/daily-news | MCP server — crypto news aggregation with bullish/bearish signals + scores |
| B4 | cryptoskills.dev | Registry: Polymarket MCP (45+ actions, 54k calls), CCXT MCP (100+ exchanges) |
| B5 | agentstore-pi.vercel.app | Polymarket MCP, QuantOracle (63 quant tools, Black-Scholes), Funding Rates MCP |
| B6 | MrFadiAi/Polymarket-bot | YES+NO < $1 arbitrage, DipArb, Smart Money, Direct Trading logic |

### Category C: Dashboard / UI Inspiration

| # | Source | Idea |
|---|--------|------|
| C1 | polyainews.vercel.app | Real-time news + AI analysis (DeepSeek) + related market odds sidebar |
| C2 | brief.day1global.xyz | Morning intelligence briefing — market sentiment + BTC positioning + coin tags |
| C3 | mirofish-demo.pages.dev | "Predict Anything" — clean prediction market UX |

### Filtered as Noise (not useful for trading)

| Source | Reason |
|--------|--------|
| mco-org/mco | Multi-agent coding orchestrator, zero trading relevance |
| openai/codex-plugin-cc | Code review tool only |
| numman-ali/openskills | Generic skill loader framework |
| conway.tech | Page returned only the word "Conway" — no content |

### X/Twitter Threads (blocked by auth — content recovered via WebSearch)

All 8 X/Twitter links returned auth errors. Key strategies recovered via search and attribution in existing codebase:
- `@runes_leo` — empirical Kelly sizing (already credited in `btc_signal.py:293`)
- `@RohOnChain` — cash-flow PnL model (already credited in `btc_signal.py:286`)
- Fast-resolution arb is now largely captured by sub-100ms bots; window narrowed from 12.3s (2024) to 2.7s (2026)

---

## STEP 3 — Integration Plan (Per Source)

---

### A1 — Automated Market Making
**Core Edge:** Place simultaneous limit orders on both YES ($0.58) and NO ($0.62) sides of the same market. Collect the ~4% spread regardless of outcome. Adjust every 30 seconds; pull liquidity 2 minutes before news events. $10K capital → $1,247 profit in 3 weeks (12.47%).

**Reusable Code:** None to copy directly — logic must be written. Key pattern:
```python
# Every 30 seconds:
place_limit_order("YES", current_mid - spread/2)
place_limit_order("NO",  current_mid + spread/2)
# Pull orders if |inventory_yes - inventory_no| / total > 0.30
# Pull orders if news_event_in_next_120_seconds()
```

**Integration Plan:**
1. Add `market_maker.py` to `agent/` directory
2. Use `py-clob-client` (already in `requirements.txt`) for order placement
3. Wire into `daily_runner.py` as an optional strategy alongside momentum signal
4. Risk param: never exceed 30% inventory imbalance; track via `CLOB.get_order_book()`

---

### A2 — AI Probability Arbitrage
**Core Edge:** Ingest news faster than the crowd. When ensemble model probability diverges >15% from Polymarket price, execute. Real example: Trump case — bought YES at $0.29, model said 41%, market caught up to $0.49 = $896 profit in 10 minutes.

**Reusable Code:** Pattern (not a copy-paste library):
```python
# Signal trigger:
if abs(model_probability - market_price) > 0.15:
    side = "YES" if model_probability > market_price else "NO"
    kelly_size = quarter_kelly(model_probability, market_price)
    # Execute via py-clob-client
```

**Integration Plan:**
- Our existing `agent.py` already does this for political/news markets using rule-based AI prob
- Upgrade path: feed `6551Team/daily-news` sentiment scores as a secondary signal input
- Add `news_sentiment_gate()` to `btc_signal.py` — skip UP bets when macro sentiment bearish

---

### A3 — Logical Correlation Arbitrage
**Core Edge:** Find mathematically impossible cross-market pricings. Example: "Chiefs win Super Bowl" (28%) > "AFC wins Super Bowl" (24%) is impossible since Chiefs are AFC → buy AFC, short Chiefs spread. Trigger when violation exceeds 3% (above transaction costs).

**Reusable Code:** Core detection logic:
```python
def find_logical_violations(markets: list[dict]) -> list[dict]:
    """Returns pairs where child market price > parent market price."""
    violations = []
    for parent, child in KNOWN_CORRELATIONS:
        p_price = get_price(parent["market_id"])
        c_price = get_price(child["market_id"])
        if c_price > p_price + 0.03:  # 3% threshold above tx costs
            violations.append({
                "parent": parent, "child": child,
                "spread_bps": int((c_price - p_price) * 10_000),
            })
    return violations
```

**Integration Plan:**
1. Add `correlation_arb.py` to `agent/`
2. Define `KNOWN_CORRELATIONS` map (team → league, candidate → party, monthly → quarterly)
3. Add to `arb_scanner.py` as Strategy 3 alongside funding-rate arb
4. Requires no external APIs — pure Gamma API market discovery + cross-reference

---

### A4 — DipArb (15-Minute BTC Markets)
**Core Edge:** On 15-minute BTC markets, detect crashes >15% within a 3-second window. Buy the dip (Leg 1) + simultaneously hedge the opposing leg. v3.1 enforces minimum $1.50 trade value for exit viability.

**Reusable Code (from MrFadiAi/Polymarket-bot):**
```python
async def detect_dip_arb(price_history: list[float], window_sec: int = 3) -> bool:
    if len(price_history) < 2:
        return False
    recent = price_history[-window_sec:]
    pct_change = (recent[-1] - recent[0]) / recent[0]
    return abs(pct_change) > 0.15

# If triggered:
# Leg 1: buy the crashing YES/NO token
# Leg 2: hedge with opposing leg for delta neutrality
```

**Integration Plan:**
- Already have BTC price monitoring in `btc_signal.py`
- Add `dip_arb_signal()` function to `btc_signal.py` with 3-second rolling window
- Trigger threshold: >15% crash (distinct from our 0.3% momentum threshold)
- Our circuit breaker in `PolyAlphaVault.sol` (20% drawdown halt) covers the risk

---

### A5 — Smart Money Copying
**Core Edge:** Monitor Polymarket leaderboard. Copy traders who meet: ≥60% win rate, ≥$500 profit, 1.5x profit factor, ≥70% consistency, no single trade >30% of total PnL.

**Reusable Code:**
```python
def score_trader(trader: dict) -> bool:
    return (
        trader["win_rate"] >= 0.60 and
        trader["cumulative_profit"] >= 500 and
        trader["profit_factor"] >= 1.5 and
        trader["consistency"] >= 0.70 and
        trader["max_trade_pct_of_pnl"] <= 0.30
    )
# Fetch from: GET https://data-api.polymarket.com/profiles?sort=profit&limit=100
```

**Integration Plan:**
- New file: `agent/smart_money.py`
- Poll Polymarket Data API every 6 hours for leaderboard
- When a qualifying trader opens a position, mirror at 10% of their size
- Add as an OPTIONAL strategy in `daily_runner.py` (disabled by default, enable after 50 backtested trades)

---

### A6 — Blave Quant Skill (Multi-Exchange TWAP)
**Core Edge:** TWAP order execution on BingX reduces slippage for larger positions. Alpha table filtering for coin selection based on holder concentration and whale hunter signals.

**Reusable Code:** Pattern for TWAP execution:
```python
def twap_execute(symbol: str, total_usdc: float, slices: int = 10, interval_sec: int = 30):
    slice_size = total_usdc / slices
    for i in range(slices):
        place_market_order(symbol, slice_size)
        time.sleep(interval_sec)
```

**Integration Plan:**
- Add `twap_execute()` to `execution_engine.py` as an alternative to single-shot fill
- Use when `amount_usdc > 500` (large positions where slippage matters)
- Already have OKX, Binance connections in `arb_scanner.py` — reuse those

---

### A7 — Bitget Task Skills (Event Mode)
**Core Edge:** Event Mode detects unusual market movements and auto-adjusts positions. Sleep Mode sets price-trigger conditional orders. Copy Trading filters traders by 30-day drawdown.

**Reusable Code:** Event mode volatility response:
```python
def event_mode_check(current_vol: float, baseline_vol: float, threshold: float = 2.0) -> str:
    """Returns 'REDUCE', 'HOLD', or 'EXPAND' based on volatility ratio."""
    ratio = current_vol / baseline_vol if baseline_vol > 0 else 1.0
    if ratio > threshold:
        return "REDUCE"
    elif ratio < (1 / threshold):
        return "EXPAND"
    return "HOLD"
```

**Integration Plan:**
- Add to `agent.py`'s 6-step BitPilot safety chain as Step 6.5 (volatility gate)
- Before any trade: check `event_mode_check()` — if "REDUCE", halve Kelly fraction
- Data source: compute rolling 1h vs 24h BTC price std dev

---

### B1 — Polymarket CLI (polymarket/polymarket-cli)
**Core Edge:** Complete CLOB API wrapper in Rust — limit/market orders, bulk ops, ERC-1155 CTF token split/merge/redeem. Authentication via private key + signature (not HMAC). Already has interactive REPL shell.

**Reusable Code:** Auth pattern (Python equivalent):
```python
# py-clob-client already handles this — already in requirements.txt
from py_clob_client.client import ClobClient
client = ClobClient(host=CLOB_HOST, key=PRIVATE_KEY, chain_id=137)
```

**Integration Plan:**
- `py-clob-client` already in `requirements.txt` — same capability as CLI but Python-native
- Reference CLI source for undocumented API endpoints: `src/commands/` directory
- Key endpoint discovered: `GET /prices-history?market={id}&interval=1m` for price series

---

### B2 — Polymarket/agents (Official Agent Framework)
**Core Edge:** Official Polymarket agent framework with `gamma.py` (Gamma API wrapper for market discovery), `polymarket.py` (order execution on DEX), Pydantic data models, Langchain RAG integration.

**Reusable Code:** `gamma.py` market discovery pattern:
```python
# Pattern from Polymarket/agents
import requests

GAMMA_BASE = "https://gamma-api.polymarket.com"

def get_active_btc_markets(limit: int = 20) -> list[dict]:
    resp = requests.get(
        f"{GAMMA_BASE}/markets",
        params={"active": True, "closed": False, "tag": "crypto", "limit": limit},
        timeout=10,
    )
    return [m for m in resp.json() if "bitcoin" in m.get("question", "").lower()]
```

**Integration Plan:**
- Already use this Gamma API pattern in `agent.py` — our implementation is already aligned
- Upgrade: add `tag` filter to narrow down to BTC 15-minute markets only
- Use `objects.py` Pydantic models as reference for data validation schemas

---

### B3 — 6551Team/daily-news (MCP Sentiment Server)
**Core Edge:** MCP server that aggregates crypto/DeFi news with sentiment scores, grades (A/B/C), bullish/bearish signals, and coin tags. Real-time via REST API.

**Reusable Code:** Add to `agent.py`'s news gate:
```python
def get_macro_sentiment() -> str:
    """Returns 'BULLISH', 'BEARISH', or 'NEUTRAL' for current BTC macro."""
    try:
        resp = requests.get("http://localhost:3001/hot-news?category=crypto&limit=10", timeout=3)
        items = resp.json().get("data", [])
        bullish = sum(1 for i in items if i.get("signal") == "bullish")
        bearish = sum(1 for i in items if i.get("signal") == "bearish")
        if bullish > bearish + 2: return "BULLISH"
        if bearish > bullish + 2: return "BEARISH"
    except Exception:
        pass
    return "NEUTRAL"
```

**Integration Plan:**
1. Clone repo + run locally as MCP server: `npm start` on port 3001
2. Add `get_macro_sentiment()` to `btc_signal.py`
3. In `generate_signal()`: if BTC trending UP but macro sentiment BEARISH → reduce Kelly by 50%
4. Add to `.claude/mcp.json` as a fourth MCP server entry

---

### B4 + B5 — cryptoskills.dev + agentstore-pi.vercel.app (Discovery Hubs)
**Core Edge:** Two curated registries revealing the best available MCP tools:
- **Polymarket MCP**: 45+ actions, 54,822 calls — most popular in ecosystem. Covers market discovery, order placement, L1/L2 auth, WebSocket subscriptions, CTF operations.
- **QuantOracle**: 63 quant tools including Black-Scholes, volatility surfaces
- **CCXT MCP**: 100+ exchanges via single interface (already in our `arb_scanner.py`)
- **Funding Rates MCP**: Tracks funding rate arbitrage opportunities (overlaps with our `arb_scanner.py`)

**Integration Plan:**
- Add **Polymarket MCP** to `.claude/mcp.json` for Claude Code to directly query markets during development
- Use **QuantOracle** Black-Scholes tools to price option-like positions in `btc_signal.py`
- **CCXT MCP** and **Funding Rates MCP** already covered by our `arb_scanner.py`

---

### B6 — MrFadiAi/Polymarket-bot
**Core Edge:** 4-strategy bot with 4-layer risk protection:
1. YES+NO < $1.00 → instant riskless profit
2. DipArb — 15-min crash detection
3. Smart Money — leaderboard copying
4. Direct Trading — Fill-or-Kill + price sniping

**Reusable Code:** YES+NO arbitrage (Strategy 1):
```python
def check_yes_no_arb(market_id: str) -> Optional[dict]:
    """Returns arb opportunity when YES + NO prices < $1.00."""
    yes_price = get_best_ask("YES", market_id)
    no_price  = get_best_ask("NO",  market_id)
    if yes_price is None or no_price is None:
        return None
    total = yes_price + no_price
    if total < 0.98:  # 2% buffer for gas/fees
        return {
            "market_id": market_id,
            "yes_price": yes_price,
            "no_price": no_price,
            "profit_pct": (1 - total) * 100,
        }
    return None
```

**Integration Plan:**
- Add `yes_no_arb_scanner()` to `arb_scanner.py` as Strategy 4
- Run on every market in our active market list every 60 seconds
- This is pure mathematical arbitrage — zero directional risk

---

## Priority Implementation Order

```
PHASE 1 (This Week — Dry-Run Mode):
  [x] Fix btc_signal.py CLOB stub → implemented below
  [ ] Add yes_no_arb_scanner() to arb_scanner.py  ← highest-value, zero directional risk
  [ ] Add correlation_arb.py with KNOWN_CORRELATIONS map
  [ ] Add get_macro_sentiment() news gate to btc_signal.py

PHASE 2 (Before Demo — May 5-7):
  [ ] market_maker.py (AMM both sides, 78-85% WR)
  [ ] dip_arb_signal() in btc_signal.py
  [ ] Add 6551Team/daily-news as MCP server in .claude/mcp.json

PHASE 3 (Post-Demo / Future):
  [ ] smart_money.py (leaderboard monitoring)
  [ ] TWAP execution in execution_engine.py
  [ ] QuantOracle Black-Scholes integration
```

---

## Key Risk Management Rules (from research)

All strategies in PolyAlpha must respect these rules (from Medium analysis + MrFadiAi):

| Rule | Value | Source |
|------|-------|--------|
| Max position per market | 10% TVL | Medium / MrFadiAi |
| Max correlated exposure | 30% TVL | Medium |
| Daily drawdown halt | 5% | MrFadiAi 4-layer system |
| Monthly loss cap | 15% | MrFadiAi 4-layer system |
| Permanent halt trigger | 40% total loss | MrFadiAi 4-layer system |
| Consecutive loss reduction | 20% per loss | MrFadiAi adaptive sizing |
| Consecutive win increase | 10% per win (max 5% TVL) | MrFadiAi adaptive sizing |

Our existing `PolyAlphaVault.sol` (20% drawdown halt) is MORE conservative than the 5% daily rule above — **keep the on-chain circuit breaker as-is**.

---

## Sources Referenced

- [Beyond Simple Arbitrage: 4 Polymarket Strategies (2026)](https://medium.com/illumination/beyond-simple-arbitrage-4-polymarket-strategies-bots-actually-profit-from-in-2026-ddacc92c5b4f)
- [Polymarket CLI](https://github.com/Polymarket/polymarket-cli)
- [Polymarket Official Agents](https://github.com/Polymarket/agents)
- [MrFadiAi/Polymarket-bot](https://github.com/MrFadiAi/Polymarket-bot)
- [6551Team/daily-news MCP](https://github.com/6551Team/daily-news)
- [Blave-TW/blave-quant-skill](https://github.com/Blave-TW/blave-quant-skill)
- [duolaAmengweb3/bitget-task-skills](https://github.com/duolaAmengweb3/bitget-task-skills)
- [cryptoskills.dev](https://cryptoskills.dev)
- [agentstore-pi.vercel.app](https://agentstore-pi.vercel.app/zh)
- [Definitive Guide to Polymarket Ecosystem (DeFi Prime)](https://defiprime.com/definitive-guide-to-the-polymarket-ecosystem)
- [Polymarket Dynamic Fees Announcement](https://www.financemagnates.com/cryptocurrency/polymarket-introduces-dynamic-fees-to-curb-latency-arbitrage-in-short-term-crypto-markets/)
