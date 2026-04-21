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
from dataclasses import dataclass
from typing import Optional

BINANCE_KLINE_URL = "https://api.binance.com/api/v3/klines"
BINANCE_PRICE_URL = "https://api.binance.com/api/v3/ticker/price"
GAMMA_API         = "https://gamma-api.polymarket.com"

# ── Signal parameters ─────────────────────────────────────────────────────────
MOMENTUM_THRESHOLD   = 0.003   # BTC must move >0.3% in 7 minutes
ODDS_MAX_FOR_ENTRY   = 0.62    # Polymarket odds must be <62% (market hasn't priced it in)
EDGE_MIN_BPS         = 800     # Minimum 8% edge (80 basis points on a 0–1 scale)
MIN_LIQUIDITY_USD    = 50_000  # Minimum $50K market liquidity
KELLY_FRACTION       = 0.25    # Quarter-Kelly
MAX_POSITION_BPS     = 500     # 5% TVL cap per position


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
        return (
            f"{'✅ SIGNAL' if self.is_valid() else '⛔ NO TRADE'} | "
            f"Side: {self.side} | "
            f"BTC Δ: {self.btc_momentum*100:+.2f}% | "
            f"Market: {self.market_price*100:.1f}% | "
            f"AI Est: {self.ai_probability*100:.1f}% | "
            f"Edge: {self.edge_bps/100:+.1f}% | "
            f"Kelly: {self.kelly_fraction*100:.1f}% TVL"
        )


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

    # Momentum-based adjustment: each 0.1% move → +3% probability
    raw_adjustment = (abs(btc_momentum) / 0.001) * 0.03
    capped_adjustment = min(raw_adjustment, 0.15)  # hard cap at +15%

    direction = 1 if btc_momentum > 0 else -1
    adjusted_prob = market_price + (direction * capped_adjustment)

    # Clamp to [0.01, 0.99]
    return max(0.01, min(0.99, adjusted_prob))


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
    market_price: float,      # Current Polymarket YES price (0–1)
    liquidity_usd: float,
    btc_open: Optional[float] = None,
    btc_now:  Optional[float] = None,
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

    # Estimate true probability
    ai_prob = btc_momentum_to_probability(relevant_price, abs(btc_momentum))

    # Edge calculation
    edge = ai_prob - relevant_price

    # Build oracle hash for on-chain integrity
    oracle_hash = build_oracle_hash(btc_open, btc_now, market_price, ts)

    # Kelly sizing
    kelly_f = quarter_kelly(ai_prob, relevant_price)

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
    print("BTC Signal Engine — Manual Test")
    print("=" * 50)

    # Simulated test: BTC moved up 0.5% in 7 minutes, market still at 55%
    test_signal = generate_signal(
        market_question = "Will Bitcoin be higher in 15 minutes? [Test]",
        condition_id    = "0xtest",
        market_price    = 0.55,   # Polymarket YES price
        liquidity_usd   = 100_000,
        btc_open        = 45_000.0,
        btc_now         = 45_225.0,  # +0.5% move
    )

    if test_signal:
        print(test_signal)
        print(f"\nOracle hash (for on-chain logging): {test_signal.oracle_hash}")
        print(f"Kelly fraction:   {test_signal.kelly_fraction*100:.2f}% of TVL")
        print(f"ai_prob_bps:      {test_signal.ai_prob_bps}  (71.00 = 71.00%)")
        print(f"market_price_bps: {test_signal.market_price_bps}")
        print(f"edge_bps:         {test_signal.edge_bps}")
    else:
        print("No signal generated (below thresholds)")
