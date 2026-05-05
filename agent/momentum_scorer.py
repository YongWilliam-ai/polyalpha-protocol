"""
momentum_scorer.py — Python port of duolaAmengweb3/bgtask momentum-scorer.ts

Three-factor momentum scoring with ATR volatility scaling:
    ROC   40%  — Rate of Change: raw price momentum
    RSI   30%  — Relative Strength Index: overbought/oversold
    MACD  30%  — MACD Histogram: trend acceleration
    ATR         — Volatility scaler from bgtask/budget-allocator.ts

Public API:
    compute_momentum_score(prices: list[float]) -> float   # range [-1.0, +1.0]
    score_to_signal(score: float) -> str                   # "UP" | "DOWN" | "HOLD"
"""

import numpy as np

# Factor weights — must sum to 1.0
ROC_WEIGHT  = 0.40
RSI_WEIGHT  = 0.30
MACD_WEIGHT = 0.30

# Indicator parameters (matching bgtask/momentum-scorer.ts defaults)
RSI_PERIOD  = 14
ROC_PERIOD  = 10
MACD_FAST   = 12
MACD_SLOW   = 26
MACD_SIGNAL = 9

# Signal classification thresholds
SIGNAL_BUY_THRESHOLD  =  0.20
SIGNAL_SELL_THRESHOLD = -0.20


def _compute_roc(prices: np.ndarray, period: int = ROC_PERIOD) -> float:
    """
    Rate of Change: (price_now - price_n_ago) / price_n_ago
    Normalized to [-1, +1] where a 20% BTC move maps to +-1.0.
    """
    if len(prices) < period + 1:
        return 0.0
    p_now  = prices[-1]
    p_prev = prices[-(period + 1)]
    if p_prev == 0:
        return 0.0
    roc = (p_now - p_prev) / p_prev
    return float(np.clip(roc / 0.20, -1.0, 1.0))


def _compute_rsi(prices: np.ndarray, period: int = RSI_PERIOD) -> float:
    """
    Wilder RSI mapped to [-1, +1]:
        RSI >= 70  ->  overbought  ->  negative score (expect reversion)
        RSI <= 30  ->  oversold    ->  positive score (expect bounce)
        RSI == 50  ->  neutral     ->  0.0
    """
    if len(prices) < period + 1:
        return 0.0
    deltas = np.diff(prices[-(period + 1):])
    gains  = np.where(deltas > 0, deltas,  0.0)
    losses = np.where(deltas < 0, -deltas, 0.0)

    avg_gain = float(np.mean(gains))
    avg_loss = float(np.mean(losses))

    if avg_loss == 0:
        rsi = 100.0 if avg_gain > 0 else 50.0
    else:
        rsi = 100.0 - (100.0 / (1.0 + avg_gain / avg_loss))

    return float(np.clip(-(rsi - 50.0) / 50.0, -1.0, 1.0))


def _ema(arr: np.ndarray, span: int) -> np.ndarray:
    """Exponential moving average with standard 2/(span+1) smoothing factor."""
    alpha  = 2.0 / (span + 1)
    result = np.empty(len(arr))
    result[0] = arr[0]
    for i in range(1, len(arr)):
        result[i] = alpha * arr[i] + (1.0 - alpha) * result[i - 1]
    return result


def _compute_macd_hist(prices: np.ndarray) -> float:
    """
    MACD Histogram = MACD_line - Signal_line.
    Normalized to [-1, +1] where 1% of current price = +-1.0 boundary.
    """
    if len(prices) < MACD_SLOW + MACD_SIGNAL:
        return 0.0
    fast_ema    = _ema(prices, MACD_FAST)
    slow_ema    = _ema(prices, MACD_SLOW)
    macd_line   = fast_ema - slow_ema
    signal_line = _ema(macd_line, MACD_SIGNAL)
    histogram   = macd_line[-1] - signal_line[-1]
    norm_factor = prices[-1] * 0.01 if prices[-1] > 0 else 1.0
    return float(np.clip(histogram / norm_factor, -1.0, 1.0))


def _compute_atr(prices: np.ndarray, period: int = 14) -> float:
    """
    Volatility proxy: standard deviation of returns over the last `period` bars.
    Used for ATR-based scaling in budget-allocator.ts.
    """
    if len(prices) < period + 1:
        return 0.01
    returns = np.diff(prices[-period:]) / prices[-period:-1]
    std = float(np.std(returns))
    return std if std > 0 else 0.01


def compute_momentum_score(prices: list) -> float:
    """
    Three-factor weighted momentum score.
    Ported from bgtask/momentum-scorer.ts with ATR volatility scaling
    from bgtask/budget-allocator.ts.

    Args:
        prices: Closing prices oldest-first. Minimum ~35 bars recommended
                for MACD to have enough history.

    Returns:
        Score in [-1.0, +1.0].
        Positive = bullish momentum, negative = bearish.
        High ATR shrinks magnitude to reduce conviction in volatile regimes.
    """
    if len(prices) < 2:
        return 0.0

    arr = np.array(prices, dtype=float)

    roc_score  = _compute_roc(arr)
    rsi_score  = _compute_rsi(arr)
    macd_score = _compute_macd_hist(arr)

    raw_score = (
        ROC_WEIGHT  * roc_score +
        RSI_WEIGHT  * rsi_score +
        MACD_WEIGHT * macd_score
    )

    # ATR-based volatility scaling (budget-allocator.ts):
    # High volatility shrinks score conviction to avoid oversizing.
    # 1% ATR -> scale ~0.91x; 5% ATR -> scale ~0.67x; 10% ATR -> scale ~0.50x
    atr       = _compute_atr(arr)
    atr_scale = 1.0 / (1.0 + atr * 10.0)

    return float(np.clip(raw_score * atr_scale, -1.0, 1.0))


def score_to_signal(score: float) -> str:
    """Classify a numeric score into a directional signal."""
    if score > SIGNAL_BUY_THRESHOLD:
        return "UP"
    if score < SIGNAL_SELL_THRESHOLD:
        return "DOWN"
    return "HOLD"
