"""
daily_runner.py -- PolyAlpha Daily Orchestrator

Runs all data collection pipelines once, persists results, prints a status line.
Designed to be called by cron (HKUST ugcpu1) or GitHub Actions.

Usage:
  cd agent && python daily_runner.py
  cd agent && python daily_runner.py --dry-run   # skip Telegram push

Output:
  reports/history.jsonl         -- one JSON record per daily run (appended)
  reports/summary_YYYY-MM-DD.json -- daily summary snapshot

Status line printed to stdout:
  [2026-04-28] Funding: REAL v | Polymarket: MOCK x | Opps: 3
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime, timezone
from pathlib import Path

# dotenv optional -- load if available
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")
except ImportError:
    pass

import requests

from arb_scanner import scan_funding_arbitrage, scan_polymarket_fast_resolution

# -- Config -------------------------------------------------------------------
REPORTS_DIR = Path(__file__).parent.parent / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

HISTORY_FILE = REPORTS_DIR / "history.jsonl"

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID", "")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("daily_runner")


# -- Telegram -----------------------------------------------------------------

def send_telegram(message: str, dry_run: bool = False) -> bool:
    if dry_run:
        log.info(f"[DRY RUN] Telegram:\n{message}")
        return True
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"},
            timeout=5,
        )
        resp.raise_for_status()
        return True
    except Exception as exc:
        log.warning(f"Telegram failed: {exc}")
        return False


# -- Data collection ----------------------------------------------------------

def get_funding_rates() -> dict:
    """Thin wrapper — standard Prompt 2 interface."""
    return scan_funding_arbitrage(min_bps=10)   # low threshold to capture more live data


def scan_polymarket(max_hours: int = 4) -> dict:
    """Thin wrapper — standard Prompt 2 interface."""
    return scan_polymarket_fast_resolution(
        min_price=0.90,
        max_hours_to_end=max_hours,
        min_volume_usd=5_000,
    )


# -- Persistence --------------------------------------------------------------

def _append_history(record: dict) -> None:
    """Append one JSON record to history.jsonl."""
    with open(HISTORY_FILE, "a") as f:
        f.write(json.dumps(record) + "\n")


def _write_summary(date_str: str, summary: dict) -> None:
    path = REPORTS_DIR / f"summary_{date_str}.json"
    with open(path, "w") as f:
        json.dump(summary, f, indent=2)
    log.info(f"Summary written: {path}")


# -- Main run -----------------------------------------------------------------

def run(dry_run: bool = False) -> dict:
    """
    Execute one daily data collection run.
    Returns the summary dict.
    """
    now       = datetime.now(timezone.utc)
    date_str  = now.strftime("%Y-%m-%d")
    ts        = now.isoformat()

    log.info(f"=== PolyAlpha Daily Runner [{date_str}] ===")

    # Collect funding rates
    log.info("Collecting funding rates...")
    try:
        funding = get_funding_rates()
    except Exception as exc:
        funding = {"data": [], "source": "mock", "timestamp": ts, "error": str(exc)}
        log.error(f"Funding collection failed: {exc}")

    # Collect PolyMarket near-settlement
    log.info("Collecting PolyMarket near-settlement scan...")
    try:
        polymarket = scan_polymarket()
    except Exception as exc:
        polymarket = {"data": [], "source": "mock", "timestamp": ts, "error": str(exc)}
        log.error(f"PolyMarket collection failed: {exc}")

    opps_count    = len(funding["data"]) + len(polymarket["data"])
    funding_src   = funding["source"]
    poly_src      = polymarket["source"]

    # Persist history record
    history_record = {
        "timestamp":        ts,
        "date":             date_str,
        "funding":          funding,
        "polymarket":       polymarket,
        "opportunities":    opps_count,
        "funding_source":   funding_src,
        "polymarket_source": poly_src,
    }
    _append_history(history_record)
    log.info(f"Appended to {HISTORY_FILE}")

    # Persist daily summary
    mock_count = sum([funding_src == "mock", poly_src == "mock"])
    mock_pct   = mock_count / 2.0

    summary = {
        "date":                  date_str,
        "funding_source":        funding_src,
        "polymarket_source":     poly_src,
        "opportunities_found":   opps_count,
        "mock_percentage":       mock_pct,
        "funding_error":         funding.get("error"),
        "polymarket_error":      polymarket.get("error"),
    }
    _write_summary(date_str, summary)

    # Status line (Prompt 2 spec)
    def _icon(src: str) -> str:
        return "REAL v" if src == "real" else "MOCK x"

    status_line = (
        f"[{date_str}] Funding: {_icon(funding_src)} | "
        f"Polymarket: {_icon(poly_src)} | Opps: {opps_count}"
    )
    print(status_line)

    # Optional Telegram daily summary
    if not dry_run and (TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID):
        msg = (
            f"*PolyAlpha Daily* -- {date_str}\n"
            f"Funding: `{funding_src.upper()}` | Polymarket: `{poly_src.upper()}`\n"
            f"Opportunities found: {opps_count}\n"
            f"Mock %: {mock_pct*100:.0f}%"
        )
        send_telegram(msg)

    return summary


# -- Entry point --------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PolyAlpha Daily Data Runner")
    parser.add_argument("--dry-run", action="store_true", help="Skip Telegram push")
    args = parser.parse_args()

    summary = run(dry_run=args.dry_run)
    sys.exit(0 if summary["opportunities_found"] >= 0 else 1)
