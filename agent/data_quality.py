"""
data_quality.py -- PolyAlpha Data Quality Monitor

Reads reports/history.jsonl, calculates:
  - real_data_rate: % of days with at least one real data source
  - consecutive_mock_days: how many recent days had 100% mock data

Sends a Telegram alert if consecutive_mock_days >= 3.

Usage:
  cd agent && python data_quality.py
  cd agent && python data_quality.py --threshold 2   # alert after 2 consecutive mock days
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

import requests

try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")
except ImportError:
    pass

# -- Config -------------------------------------------------------------------
REPORTS_DIR  = Path(__file__).parent.parent / "reports"
HISTORY_FILE = REPORTS_DIR / "history.jsonl"

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID", "")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("data_quality")


# -- Telegram -----------------------------------------------------------------

def send_telegram(message: str) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log.warning("Telegram not configured -- skipping alert")
        return False
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"},
            timeout=5,
        )
        resp.raise_for_status()
        log.info("Telegram alert sent")
        return True
    except Exception as exc:
        log.warning(f"Telegram failed: {exc}")
        return False


# -- Data loading -------------------------------------------------------------

def load_history() -> list[dict]:
    """Load all records from history.jsonl. Returns [] if file missing."""
    if not HISTORY_FILE.exists():
        log.warning(f"History file not found: {HISTORY_FILE}")
        return []
    records = []
    with open(HISTORY_FILE) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return records


# -- Quality metrics ----------------------------------------------------------

def compute_quality(records: list[dict]) -> dict:
    """
    Compute data quality metrics from history records.

    Returns:
        {
          "total_days": int,
          "real_data_days": int,        -- days with >= 1 real source
          "full_mock_days": int,         -- days with 100% mock sources
          "real_data_rate": float,       -- 0.0-1.0
          "consecutive_mock_days": int,  -- current streak of full-mock days
          "dates_analyzed": list[str],
        }
    """
    if not records:
        return {
            "total_days": 0,
            "real_data_days": 0,
            "full_mock_days": 0,
            "real_data_rate": 0.0,
            "consecutive_mock_days": 0,
            "dates_analyzed": [],
        }

    # Aggregate by date (latest record per date wins)
    by_date: dict[str, dict] = {}
    for rec in records:
        date = rec.get("date") or rec.get("timestamp", "")[:10]
        if date:
            by_date[date] = rec

    sorted_dates = sorted(by_date.keys())
    total_days     = len(sorted_dates)
    real_data_days = 0
    full_mock_days = 0

    for date in sorted_dates:
        rec       = by_date[date]
        f_src     = rec.get("funding_source", "mock")
        p_src     = rec.get("polymarket_source", "mock")
        has_real  = (f_src == "real" or p_src == "real")

        if has_real:
            real_data_days += 1
        else:
            full_mock_days += 1

    # Consecutive mock days (counting from the most recent date backwards)
    consecutive_mock = 0
    for date in reversed(sorted_dates):
        rec   = by_date[date]
        f_src = rec.get("funding_source", "mock")
        p_src = rec.get("polymarket_source", "mock")
        if f_src != "real" and p_src != "real":
            consecutive_mock += 1
        else:
            break

    return {
        "total_days":             total_days,
        "real_data_days":         real_data_days,
        "full_mock_days":         full_mock_days,
        "real_data_rate":         round(real_data_days / total_days, 4) if total_days else 0.0,
        "consecutive_mock_days":  consecutive_mock,
        "dates_analyzed":         sorted_dates,
    }


# -- Main ---------------------------------------------------------------------

def run(consecutive_threshold: int = 3) -> dict:
    """
    Run quality check. Sends Telegram alert if consecutive mock days >= threshold.
    Returns the quality metrics dict.
    """
    log.info(f"=== PolyAlpha Data Quality Monitor (threshold={consecutive_threshold}d) ===")

    records = load_history()
    metrics = compute_quality(records)

    total  = metrics["total_days"]
    real   = metrics["real_data_days"]
    streak = metrics["consecutive_mock_days"]
    rate   = metrics["real_data_rate"] * 100

    log.info(f"History: {total} day(s) analyzed")
    log.info(f"Real data days: {real}/{total} ({rate:.1f}%)")
    log.info(f"Consecutive mock days (current streak): {streak}")

    if total == 0:
        log.warning("No history data yet -- run daily_runner.py first")
        return metrics

    print(
        f"\nData Quality Report\n"
        f"  Total days tracked:      {total}\n"
        f"  Real data rate:          {rate:.1f}%\n"
        f"  Consecutive mock days:   {streak}\n"
        f"  Alert threshold:         {consecutive_threshold} days"
    )

    if streak >= consecutive_threshold:
        alert_msg = (
            f"*PolyAlpha* -- Data Quality Alert\n"
            f"WARNING: {streak} consecutive day(s) of mock data.\n"
            f"Real data rate: {rate:.1f}% ({real}/{total} days)\n"
            f"Action required: check OKX / Binance / Gamma API connectivity."
        )
        log.warning(f"ALERT: {streak} consecutive mock days >= threshold {consecutive_threshold}")
        send_telegram(alert_msg)
    else:
        log.info(f"OK: consecutive mock streak ({streak}) below threshold ({consecutive_threshold})")

    return metrics


# -- Entry point --------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PolyAlpha Data Quality Monitor")
    parser.add_argument(
        "--threshold", type=int, default=3,
        help="Alert if consecutive mock days >= N (default: 3)"
    )
    args = parser.parse_args()

    metrics = run(consecutive_threshold=args.threshold)
    sys.exit(0 if metrics["consecutive_mock_days"] < args.threshold else 1)
