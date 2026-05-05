"""
safety_gate.py — Python port of duolaAmengweb3/bgtask safety-gate.ts

6-step pre-trade safety gate for the PolyAlpha daemon.
Must be called BEFORE any trade execution in pm_arb_agent.py and agent.py.

Steps ported from bgtask/safety-gate.ts:
    1. Danger symbol check     — block DANGER-class instruments
    2. Dry-run passthrough     — allow through without counting toward limits
    3. Daily trade cap         — max 5 trades per calendar day
    4. Position size ratio     — amount / total_assets must be <= 10%
    5. Order size threshold    — reject orders above $1,000 in daemon mode
    6. All-clear               — log, increment counter, return True

Public API:
    run_safety_checks(amount_usdt, total_assets, symbol, side, dry_run=False) -> bool
"""

import json
import logging
from datetime import date
from pathlib import Path

log = logging.getLogger("safety_gate")

DAILY_TRADES_FILE  = Path(__file__).parent / "logs" / "daily_trades.json"
MAX_DAILY_TRADES   = 5
MAX_POSITION_RATIO = 0.10    # 10% of total assets per single position
MAX_ORDER_USDT     = 1_000   # daemon auto-rejects orders above this threshold

DANGER_SYMBOLS = frozenset({"UNKNOWN", "SCAM", "TEST_DANGER"})


def _load_daily_trades() -> dict:
    """Read daily_trades.json, return {date_str: trade_count}. Empty dict on missing/corrupt."""
    if not DAILY_TRADES_FILE.exists():
        return {}
    try:
        return json.loads(DAILY_TRADES_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _increment_daily_trade(today: str) -> None:
    """Atomically increment today's trade counter in daily_trades.json."""
    DAILY_TRADES_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = _load_daily_trades()
    data[today] = data.get(today, 0) + 1
    DAILY_TRADES_FILE.write_text(json.dumps(data, indent=2))


def run_safety_checks(
    amount_usdt: float,
    total_assets: float,
    symbol: str,
    side: str,
    dry_run: bool = False,
) -> bool:
    """
    6-step safety gate ported from duolaAmengweb3/bgtask safety-gate.ts.

    Args:
        amount_usdt:  Size of the proposed order in USDC.
        total_assets: Current portfolio total assets in USDC.
        symbol:       Market/asset symbol (e.g. "BTC", "POLYMARKET").
        side:         Trade direction ("BUY", "SELL", "BUY_YES", etc.).
        dry_run:      If True, passes step 2 without incrementing daily counter.

    Returns:
        True  — all checks passed, safe to proceed.
        False — at least one check failed, abort the trade.
    """
    today = str(date.today())

    # Step 1: Danger symbol — block DANGER-class instruments entirely
    if symbol.upper() in DANGER_SYMBOLS:
        log.warning(f"[SafetyGate 1/6] BLOCKED — {symbol} is DANGER-class instrument")
        return False

    # Step 2: Dry-run passthrough (no real execution, counter not incremented)
    if dry_run:
        log.info(
            f"[SafetyGate 2/6] DRY RUN — passthrough for {side} {symbol} ${amount_usdt:.2f}"
        )
        return True

    # Step 3: Daily trade count cap
    daily = _load_daily_trades()
    count_today = daily.get(today, 0)
    if count_today >= MAX_DAILY_TRADES:
        log.warning(
            f"[SafetyGate 3/6] BLOCKED — daily limit reached "
            f"({count_today}/{MAX_DAILY_TRADES} trades today)"
        )
        return False

    # Step 4: Position size ratio (single position <= 10% of portfolio)
    if total_assets > 0 and (amount_usdt / total_assets) > MAX_POSITION_RATIO:
        ratio_pct = (amount_usdt / total_assets) * 100
        log.warning(
            f"[SafetyGate 4/6] BLOCKED — position {ratio_pct:.1f}% exceeds "
            f"{MAX_POSITION_RATIO * 100:.0f}% max per trade"
        )
        return False

    # Step 5: Order size threshold (daemon auto-rejects large orders)
    if amount_usdt > MAX_ORDER_USDT:
        log.warning(
            f"[SafetyGate 5/6] BLOCKED — order ${amount_usdt:.0f} exceeds "
            f"daemon auto-limit ${MAX_ORDER_USDT}"
        )
        return False

    # Step 6: All clear — log, increment daily counter, approve
    _increment_daily_trade(today)
    log.info(
        f"[SafetyGate 6/6] CLEARED — {side} {symbol} ${amount_usdt:.2f} "
        f"(trade {count_today + 1}/{MAX_DAILY_TRADES} today)"
    )
    return True
