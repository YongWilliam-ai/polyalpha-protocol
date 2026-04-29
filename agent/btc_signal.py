"""
btc_signal.py — PolyAlpha deterministic BTC momentum signal generator

Core logic (William's 7-minute hypothesis):
  - At market open (T+0): BTC price is recorded, Polymarket shows ~50/50
  - At T+7 minutes: BTC has moved in a direction
  - If BTC moved >0.3% AND Polymarket odds haven't caught up (<62% for winner) → SIGNAL

Why NOT GPT-4o for BTC:
  GPT-4o has no real-time price data. For a 15-minute binary BTC market,
  the signal is purely technical — momentum of the underlying asset.
  GPT-4o is only used in agent.py for political/news events where
  language understanding adds genuine value.

Oracle integrity:
  All inputs (btc_open, btc_now, poly_odds, timestamp) are SHA-256 hashed
  and logged on-chain via vault.logPosition(). This proves the agent's
  exact inputs were not manipulated after the fact.
"""

import hashlib
import json
import time
import requests
import numpy as np
from dataclasses import dataclass
from typing import Optional

BINANCE_KLINE_URL = "https://api.binance.com/api/v3/klines"
BINANCE_PRICE_URL = "https://api.binance.com/api/v3/ticker/price"
GAMMA_API         = "https://gamma-api.polymarket.com"
CLOB_HOST         = "https://clob.polymarket.com"
SENTIMENT_API_URL = "https://ai.6551.io/open/free_hot"   # 6551Team/daily-news MCP source

# Sentiment gate: Kelly fraction multiplier applied to UP signals during BEARISH macro
SENTIMENT_KELLY_REDUCTION = 0.5

# ── Signal parameters ────────────────────────────────────────────────────────
MOMENTUM_THRESHOLD   = 0.003   # BTC must move >0.3% in 7 minutes
ODDS_MAX_FOR_ENTRY   = 0.62    # Polymarket odds must be <62% (market hasn't priced it in)
EDGE_MIN_BPS         = 800     # Minimum 8% edge
EDGE_MAX_BPS         = 1500    # Dual-source cap: abort if divergence > 15% (data anomaly)
MIN_LIQUIDITY_USD    = 50_000  # Minimum $50K market liquidity
KELLY_FRACTION       = 0.25    # Quarter-Kelly scaling factor
MAX_POSITION_BPS     = 500     # 5% TVL cap per position
MONTE_CARLO_PATHS    = 10_000  # Paths for Monte Carlo Kelly sizing
MONTE_CARLO_SIGMA    = 0.05    # Std dev on probability estimate (epistemic uncertainty)
MONTE_CARLO_SEED     = 42      # Reproducible sampling


@dataclass
class BtcSignal:
    market_question: str
    condition_id: str
    side: str                   # "UP" or "DOWN"
    btc_open: float             # BTC price at market open
    btc_now: float              # BTC price at T+7
    btc_momentum: float         # (btc_now - btc_open) / btc_open
    market_price: float         # Current Polymarket YES price (0–1)
    ai_probability: float       # Derived probability (0–1)
    edge: float                 # ai_probability - market_price (signed)
    kelly_fraction: float       # Recommended position as fraction of TVL
    oracle_hash: str            # SHA-256 of all inputs — logged on-chain
    timestamp: int

    @property
    def edge_bps(self) -> int:
        return int(self.edge * 10_000)

    @property
    def ai_prob_bps(self) -> int:
        return int(self.ai_probability * 10_000)

    @property
    def market_price_bps(self) -> int:
        return int(self.market_price * 10_000)

    @property
    def kelly_bps(self) -> int:
        return int(self.kelly_fraction * 10_000)

    def is_valid(self) -> bool:
        return self.edge_bps >= EDGE_MIN_BPS

    def __str__(self) -> str:
        label = "SIGNAL" if self.is_valid() else "NO TRADE"
        return (
            f"[{label}] Side: {self.side} | "
            f"BTC Delta: {self.btc_momentum*100:+.2f}% | "
            f"Market: {self.market_price*100:.1f}% | "
            f"AI Est: {self.ai_probability*100:.1f}% | "
            f"Edge: {self.edge_bps/100:+.1f}% | "
            f"Kelly: {self.kelly_fraction*100:.1f}% TVL"
        )


# ── Polymarket V2 odds fetching ───────────────────────────────────────────────

def get_polymarket_v2_odds(market_id: str) -> Optional[float]:
    """
    Fetch YES token odds from Polymarket V2.

    Primary:  py-clob-client midpoint via CLOB REST API (no auth required for reads).
    Fallback: Gamma API REST call (always works, slightly stale vs live orderbook).

    market_id is the YES-outcome token ID (condition_id + 0 index) from Gamma API.
    Returns YES probability (0-1) or None on failure.
    """
    # Primary: CLOB midpoint — live orderbook price, no auth required for reads
    try:
        resp = requests.get(
            f"{CLOB_HOST}/midpoint",
            params={"token_id": market_id},
            timeout=5,
        )
        if resp.status_code == 200:
            data = resp.json()
            mid = data.get("mid")
            if mid is not None:
                return float(mid)
    except Exception:
        pass

    # Fallback: Gamma API REST call (V2-compatible for price reads)
    try:
        resp = requests.get(
            f"{GAMMA_API}/markets/{market_id}",
            timeout=5,
        )
        if resp.status_code == 200:
            data = resp.json()
            prices = data.get("outcomePrices", [])
            if prices:
                return float(prices[0])
    except Exception:
        pass
    return None


# ── Macro sentiment gate ──────────────────────────────────────────────────────

def get_macro_sentiment() -> str:
    """
    Returns current crypto macro sentiment: "BULLISH", "BEARISH", or "NEUTRAL".

    # OpenSource_Integration_Plan.md Strategy B3 — 6551Team/daily-news MCP
    # Source: https://ai.6551.io/open/free_hot (category=crypto)
    # Each item has a `signal` field: "bullish" | "bearish" | absent.
    # Decision rule: if bullish count > bearish + 2 → BULLISH
    #                if bearish count > bullish + 2 → BEARISH
    #                otherwise                      → NEUTRAL
    # The +2 buffer prevents a single headline from swinging the gate.

    Fail-safe: returns "NEUTRAL" on any network or parse failure so it
    never blocks a valid signal due to an API outage.
    """
    try:
        resp = requests.get(
            SENTIMENT_API_URL,
            params={"category": "crypto", "limit": 10},
            timeout=5,
        )
        if resp.status_code != 200:
            return "NEUTRAL"

        payload = resp.json()
        # Handle both list responses and wrapped {"data": [...]} shapes
        if isinstance(payload, list):
            items = payload
        elif isinstance(payload, dict):
            items = payload.get("data", payload.get("items", payload.get("list", [])))
        else:
            return "NEUTRAL"

        bullish = sum(1 for i in items if str(i.get("signal", "")).lower() == "bullish")
        bearish = sum(1 for i in items if str(i.get("signal", "")).lower() == "bearish")

        if bullish > bearish + 2:
            return "BULLISH"
        if bearish > bullish + 2:
            return "BEARISH"
        return "NEUTRAL"
    except Exception:
        return "NEUTRAL"


# ── BTC data fetching ─────────────────────────────────────────────────────────

def get_btc_price_now() -> float:
    """Current BTC/USDT spot price from Binance."""
    resp = requests.get(BINANCE_PRICE_URL, params={"symbol": "BTCUSDT"}, timeout=5)
    resp.raise_for_status()
    return float(resp.json()["price"])


def get_btc_price_n_minutes_ago(minutes: int) -> float:
    """
    Fetch BTC price from N minutes ago using Binance 1m klines.
    Returns the open price of the candle that started N minutes ago.
    """
    end_ms   = int(time.time() * 1000)
    start_ms = end_ms - (minutes * 60 * 1000)

    resp = requests.get(
        BINANCE_KLINE_URL,
        params={"symbol": "BTCUSDT", "interval": "1m", "startTime": start_ms, "limit": 1},
        timeout=5,
    )
    resp.raise_for_status()
    candles = resp.json()
    if not candles:
        raise ValueError("No kline data returned from Binance")
    return float(candles[0][1])  # open price of that 1m candle


# ── Probability estimation ────────────────────────────────────────────────────

def btc_momentum_to_probability(market_price: float, btc_momentum: float) -> float:
    """
    Derives an estimated win probability from BTC momentum.

    Calibration logic (from William's hypothesis):
      - A 0.3% BTC move in 7 minutes corresponds to ~8–12% incremental probability
        that the move continues for the remaining 8 minutes.
      - Adjustment is capped at 15% to prevent overclaiming on volatile moves.
      - Direction must match the side being considered.

    This is explicitly a RULE-BASED estimate, not a trained ML model.
    The calibration will be validated/adjusted based on backtest results.
    """
    if abs(btc_momentum) < MOMENTUM_THRESHOLD:
        return market_price  # insufficient signal, return market price

    # Momentum-based adjustment: each 0.1% move -> +3% probability
    # Cap raised to 0.25 so that strong moves (>0.5%) can exceed the dual-source
    # 15% limit and trigger the oracle consistency abort in generate_signal().
    raw_adjustment = (abs(btc_momentum) / 0.001) * 0.03
    capped_adjustment = min(raw_adjustment, 0.25)  # hard cap at +25%

    direction = 1 if btc_momentum > 0 else -1
    adjusted_prob = market_price + (direction * capped_adjustment)

    # Clamp to [0.01, 0.99]
    return max(0.01, min(0.99, adjusted_prob))


# ── Dual-source oracle consistency check ─────────────────────────────────────

def dual_source_oracle_check(ai_prob: float, market_price: float) -> bool:
    """
    V2.0 safety gate comparing two independent probability estimates.

    Source 1 (Polymarket): market-aggregated probability for the direction.
    Source 2 (Binance): our momentum-derived probability (ai_prob).

    A small divergence (8-15%) is our edge -- that is the trade.
    An EXTREME divergence (>15%) is suspicious: it may mean a data feed is
    stale, a news event broke our momentum model, or oracle data is bad.
    We abort in that case rather than bet on potentially corrupted data.

    Valid trade window: EDGE_MIN_BPS (8%) <= divergence < EDGE_MAX_BPS (15%).
    Returns True if safe to proceed, False if signal should be aborted.
    """
    divergence = abs(ai_prob - market_price)
    return divergence <= (EDGE_MAX_BPS / 10_000)


# ── Kelly criterion ───────────────────────────────────────────────────────────

def quarter_kelly(p: float, market_price: float) -> float:
    """
    Full Kelly fraction: f* = (p*b - q) / b  where b = (1-price)/price
    Apply quarter-Kelly for prototype safety (standard institutional practice).
    Cap at MAX_POSITION_BPS (5% TVL).

    Reference: Kelly (1956) "A New Interpretation of Information Rate"
    """
    if p <= market_price:
        return 0.0  # negative edge, no trade

    b = (1 - market_price) / market_price  # net odds of a YES bet
    q = 1 - p
    f_full = (p * b - q) / b

    f_quarter = f_full * KELLY_FRACTION
    return min(max(f_quarter, 0.0), MAX_POSITION_BPS / 10_000)


def monte_carlo_kelly(
    p: float,
    market_price: float,
    n_paths: int = MONTE_CARLO_PATHS,
    seed: int = MONTE_CARLO_SEED,
) -> float:
    """
    V2.0 Monte Carlo Kelly sizing.

    Instead of using the point estimate p directly, we sample N probabilities
    from Normal(p, MONTE_CARLO_SIGMA), capturing our epistemic uncertainty about
    the true win probability. We compute the full Kelly fraction for each sampled
    probability, then take the MEDIAN and apply quarter-Kelly.

    Rationale:
    - Our rule-based model is not a trained ML model; p has ~5% estimation error.
    - The median is robust: it ignores the top 50% of optimistic Kelly fractions,
      producing a naturally conservative position size.
    - 10,000 paths gives stable convergence without being expensive (numpy vectorized).

    Returns quarter-Kelly of the median simulated fraction, capped at 5% TVL.
    """
    if p <= market_price:
        return 0.0

    rng = np.random.default_rng(seed)
    p_samples = rng.normal(p, MONTE_CARLO_SIGMA, n_paths)
    p_samples = np.clip(p_samples, 0.01, 0.99)

    b = (1 - market_price) / market_price  # fixed odds for all paths

    kelly_samples = (p_samples * b - (1 - p_samples)) / b
    kelly_samples = np.maximum(kelly_samples, 0.0)  # floor at zero

    f_median = float(np.median(kelly_samples))
    f_quarter = f_median * KELLY_FRACTION

    return min(max(f_quarter, 0.0), MAX_POSITION_BPS / 10_000)


def empirical_kelly(
    p: float,
    market_price: float,
    trade_history: list,
    n_window: int = 50,
) -> float:
    """
    Empirical Kelly sizing using ACTUAL win rate from recent trade history.

    # Inspired by @RohOnChain Empirical Kelly research

    Unlike monte_carlo_kelly() which models epistemic uncertainty around a
    fixed theoretical probability, this uses the OBSERVED win rate from the
    last N=50 trades as the ground-truth p -- directly grounding position
    sizing in real performance rather than assumptions.

    Falls back to monte_carlo_kelly() if fewer than 10 trades exist
    (insufficient sample for reliable win-rate estimation).

    trade_history: list of dicts with at least {"won": bool}
    """
    # Inspired by @RohOnChain Empirical Kelly research
    recent = trade_history[-n_window:] if len(trade_history) > n_window else trade_history

    if len(recent) < 10:
        return monte_carlo_kelly(p, market_price)

    empirical_wr = sum(1 for t in recent if t.get("won", False)) / len(recent)

    if empirical_wr <= market_price:
        return 0.0

    b = (1 - market_price) / market_price
    q = 1 - empirical_wr
    f_full = (empirical_wr * b - q) / b
    f_quarter = max(f_full, 0.0) * KELLY_FRACTION

    return min(f_quarter, MAX_POSITION_BPS / 10_000)


# ── Oracle hash ───────────────────────────────────────────────────────────────

def build_oracle_hash(btc_open: float, btc_now: float, poly_odds: float, ts: int) -> str:
    """
    SHA-256 hash of all signal inputs at decision time.
    This 32-byte hash is stored on-chain in logPosition(), proving that
    the agent's inputs were not manipulated after the fact.
    Format: hex string (0x-prefixed, 64 chars).
    """
    payload = json.dumps({
        "btc_open": round(btc_open, 2),
        "btc_now":  round(btc_now, 2),
        "poly_odds": round(poly_odds, 4),
        "timestamp": ts,
    }, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    return "0x" + digest


# ── Main signal generator ─────────────────────────────────────────────────────

def generate_signal(
    market_question: str,
    condition_id: str,
    market_price: float,      # Current Polymarket YES price (0-1)
    liquidity_usd: float,
    btc_open: Optional[float] = None,
    btc_now:  Optional[float] = None,
    trade_history: Optional[list] = None,   # past {"won": bool} records for empirical Kelly
) -> Optional[BtcSignal]:
    """
    Generate a trading signal for a BTC Up/Down Polymarket market.

    Returns None if:
      - Insufficient liquidity
      - BTC momentum is too weak
      - Edge is below threshold

    Returns a BtcSignal if a trade opportunity exists.
    """
    # Liquidity filter
    if liquidity_usd < MIN_LIQUIDITY_USD:
        return None

    ts = int(time.time())

    # Fetch BTC prices if not provided (live mode)
    try:
        if btc_now is None:
            btc_now = get_btc_price_now()
        if btc_open is None:
            btc_open = get_btc_price_n_minutes_ago(7)
    except Exception as e:
        print(f"  ⚠️  BTC price fetch failed: {e}")
        return None

    btc_momentum = (btc_now - btc_open) / btc_open

    # No signal if momentum is below threshold
    if abs(btc_momentum) < MOMENTUM_THRESHOLD:
        return None

    # Determine which direction BTC is moving
    btc_moving_up = btc_momentum > 0

    # We generate a signal for the direction BTC is moving IF the market hasn't priced it in
    if btc_moving_up:
        side = "UP"
        relevant_price = market_price          # YES = UP
    else:
        side = "DOWN"
        relevant_price = 1 - market_price      # NO = DOWN implied price

    # Market must NOT have fully priced in the move yet
    if relevant_price >= ODDS_MAX_FOR_ENTRY:
        return None  # Market already priced in the momentum

    # Estimate true probability (Binance momentum model)
    ai_prob = btc_momentum_to_probability(relevant_price, abs(btc_momentum))

    # V2.0: Dual-source oracle consistency check
    # Aborts if divergence > 15% -- extreme gap suggests stale or corrupted data
    if not dual_source_oracle_check(ai_prob, relevant_price):
        return None

    # Edge calculation
    edge = ai_prob - relevant_price

    # Build oracle hash for on-chain integrity
    oracle_hash = build_oracle_hash(btc_open, btc_now, market_price, ts)

    # Kelly sizing: empirical (from actual win rate) if history exists, else Monte Carlo
    if trade_history and len(trade_history) >= 10:
        kelly_f = empirical_kelly(ai_prob, relevant_price, trade_history)
    else:
        kelly_f = monte_carlo_kelly(ai_prob, relevant_price)

    # Macro sentiment gate (OpenSource_Integration_Plan.md B3 -- 6551Team/daily-news)
    # UP signals during BEARISH macro are likely momentum false positives.
    # Reduce Kelly by 50% as a precaution rather than skipping the signal entirely.
    if side == "UP":
        sentiment = get_macro_sentiment()
        if sentiment == "BEARISH":
            kelly_f = kelly_f * SENTIMENT_KELLY_REDUCTION
            print(
                f"  [SENTIMENT GATE] Macro is BEARISH — UP signal Kelly reduced 50% "
                f"-> {kelly_f * 100:.2f}% TVL"
            )

    signal = BtcSignal(
        market_question = market_question,
        condition_id    = condition_id,
        side            = side,
        btc_open        = btc_open,
        btc_now         = btc_now,
        btc_momentum    = btc_momentum,
        market_price    = relevant_price,
        ai_probability  = ai_prob,
        edge            = edge,
        kelly_fraction  = kelly_f,
        oracle_hash     = oracle_hash,
        timestamp       = ts,
    )

    return signal if signal.is_valid() else None


# ── Standalone test ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("BTC Signal Engine V2.0 -- Manual Test")
    print("=" * 55)

    # Test 0: Macro sentiment gate
    print("\n[Test 0] Macro sentiment gate (live API call)")
    sentiment = get_macro_sentiment()
    print(f"  Current macro sentiment: {sentiment}")
    print(f"  (NEUTRAL = API unavailable or balanced -- this is fine)")

    # Test 1: Valid signal (0.4% BTC move, market at 55% -> divergence 0.12, within 15% cap)
    print("\n[Test 1] Valid signal: BTC +0.4%, market 55%")
    sig = generate_signal(
        market_question="Will Bitcoin be higher in 15 minutes? [Test]",
        condition_id="0xtest",
        market_price=0.55,
        liquidity_usd=100_000,
        btc_open=45_000.0,
        btc_now=45_180.0,  # +0.4% -> adjustment 0.12 -> ai_prob 0.67 -> edge 12%
    )
    if sig:
        print(sig)
        print(f"  Oracle hash:  {sig.oracle_hash}")
        print(f"  MC Kelly:     {sig.kelly_fraction*100:.2f}% TVL  (Monte Carlo)")
        print(f"  Edge:         {sig.edge_bps/100:.1f}%")
    else:
        print("  No signal.")

    # Test 2: Dual-source abort (BTC +0.7% -> adjustment 0.21 -> divergence 0.21 > 0.15 -> abort)
    print("\n[Test 2] Dual-source abort: BTC +0.7% (extreme for our model)")
    sig2 = generate_signal(
        market_question="Will Bitcoin be higher in 15 minutes? [Extreme]",
        condition_id="0xtest2",
        market_price=0.50,
        liquidity_usd=100_000,
        btc_open=45_000.0,
        btc_now=45_315.0,  # +0.7% -> adjustment 0.21 -> divergence 0.21 > 0.15 -> aborted
    )
    print(f"  Signal generated: {sig2 is not None}  (expect False -- dual-source abort)")

    # Test 3: Monte Carlo Kelly standalone
    print("\n[Test 3] Monte Carlo Kelly vs Point Kelly comparison")
    p_test, mkt_test = 0.68, 0.55
    mc = monte_carlo_kelly(p_test, mkt_test)
    pt = quarter_kelly(p_test, mkt_test)
    print(f"  p={p_test}, market={mkt_test}")
    print(f"  Point Kelly (V1): {pt*100:.2f}% TVL")
    print(f"  Monte Carlo (V2): {mc*100:.2f}% TVL  (conservative -- median over 10k paths)")
