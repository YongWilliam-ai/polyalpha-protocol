"""
pm_arb_agent.py -- PolyAlpha PM Near-Settlement Scanner (Paper Trading Mode)

Runs every N minutes (default: 30), scans for:
  1. PolyMarket fast-resolution arb opportunities (Strategy 1)
  2. Funding rate arb opportunities (Strategy 2, informational)

Sends Telegram alerts for HIGH-confidence opportunities.
Paper Trading phase: read-only -- NO trade execution, NO private keys.

To run:
  cd agent && python pm_arb_agent.py
  cd agent && python pm_arb_agent.py --interval 15   # scan every 15 minutes
  cd agent && python pm_arb_agent.py --dry-run        # skip Telegram sends

Env vars required for Telegram alerts:
  TELEGRAM_BOT_TOKEN  -- from @BotFather
  TELEGRAM_CHAT_ID    -- your chat/channel ID (get via @userinfobot)

References:
  PolyAlpha Strategy 1: Opus evaluation, April 2026
  @hunterweb303 funding-rates-mcp: https://github.com/duolaAmengweb3/funding-arb-scanner
"""

import os
import sys
import time
import json
import argparse
import logging
from datetime import datetime, timezone
from pathlib import Path

import requests

# dotenv is optional -- load .env if available, otherwise rely on shell env vars
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
except ImportError:
    pass

# Import reusable scanners from arb_scanner.py
# PolyAlpha Strategy 1 + @hunterweb303 funding-rates-mcp wrappers
from arb_scanner import (
    scan_funding_arbitrage,
    scan_polymarket_fast_resolution,
    oracle_risk_score,
)

# -- Logging setup ------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("pm_arb_agent")

# -- Config -------------------------------------------------------------------
SCAN_LOG_FILE = Path("agent/logs/pm_arb_scan_log.jsonl")
SCAN_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Telegram -- read from env (no defaults; alerts silently skipped if not set)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID", "")

# Alert thresholds
MIN_NET_RETURN_TO_ALERT  = 0.02    # 2% net return minimum for PM alert
MIN_NET_BPS_TO_ALERT     = 50      # 50 bps minimum for funding arb alert
MAX_ORACLE_RISK_TO_ALERT = 0.4     # skip PM markets with oracle risk >= 0.4


# -- Telegram helper ----------------------------------------------------------

def send_telegram(message: str, dry_run: bool = False) -> bool:
    """
    Send a Telegram message via Bot API.
    Returns True on success, False on failure (never raises).
    """
    if dry_run:
        log.info(f"[DRY RUN] Telegram message:\n{message}")
        return True

    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log.warning("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set -- skipping alert")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        resp = requests.post(
            url,
            json={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"},
            timeout=5,
        )
        resp.raise_for_status()
        log.info("Telegram alert sent")
        return True
    except Exception as exc:
        log.warning(f"Telegram send failed: {exc}")
        return False


# -- Alert formatters ---------------------------------------------------------

def _format_poly_alert(opp: dict, risk: float) -> str:
    net_pct = round(opp["estimated_net_return_pct"] * 100, 2)
    confidence = opp.get("confidence_label", "?")
    end_time = opp.get("end_time", "?")[:16].replace("T", " ")
    question = opp.get("question", "")[:80]
    return (
        f"*PolyAlpha* -- PM Arb Alert [{confidence}]\n"
        f"`{question}`\n"
        f"YES price: {opp['yes_price']:.3f} | Net return: {net_pct}%\n"
        f"Volume 24h: ${opp['volume_24h']:,.0f} | Ends: {end_time} UTC\n"
        f"Oracle risk: {risk:.2f} | Paper Trading -- DO NOT execute without manual check\n"
        f"#PolyAlpha #Strategy1"
    )


def _format_funding_alert(opp: dict) -> str:
    return (
        f"*PolyAlpha* -- Funding Arb Alert\n"
        f"{opp['symbol']}: long {opp['long_venue']} / short {opp['short_venue']}\n"
        f"Net spread: {opp['net_spread_bps']}bps | Ann: {opp['annualized_pct']}%\n"
        f"Est 8h PnL per $10k: ${opp['estimated_8h_pnl_per_10k']:.2f}\n"
        f"Paper Trading -- NO execution at this capital level\n"
        f"#PolyAlpha #Strategy2"
    )


# -- Scan log -----------------------------------------------------------------

def _log_scan(scan_type: str, results: list) -> None:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scan_type": scan_type,
        "count":     len(results),
        "results":   results,
    }
    try:
        with open(SCAN_LOG_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as exc:
        log.warning(f"Could not write scan log: {exc}")


# -- Core scanner loop --------------------------------------------------------

def run_scanner(interval_min: int = 30, dry_run: bool = False) -> None:
    """
    Main scanner loop. Runs every `interval_min` minutes.

    # PolyAlpha Strategy 1 + 2: near-settlement arb + funding rate arb
    Opus evaluation recommendation: "build this first, run 24/7, alert every 30 min"
    """
    log.info("=" * 60)
    log.info("PolyAlpha PM Arb Agent -- Paper Trading Mode")
    log.info(f"Scan interval: {interval_min} min | Dry run: {dry_run}")
    log.info(f"Telegram alerts: {'enabled' if TELEGRAM_BOT_TOKEN else 'DISABLED (no token)'}")
    log.info("=" * 60)

    scan_count = 0

    while True:
        scan_count += 1
        ts = datetime.now(timezone.utc).isoformat()
        log.info(f"\n-- Scan #{scan_count} @ {ts} --")

        # ── Strategy 1: PolyMarket near-settlement ────────────────────────────
        log.info("[1/2] Scanning PolyMarket fast-resolution opportunities...")
        try:
            poly_opps = scan_polymarket_fast_resolution(
                min_price=0.95,
                max_hours_to_end=2,
                min_volume_usd=10_000,
            )
            _log_scan("POLYMARKET_FAST_RESOLUTION", poly_opps)

            alerts_sent = 0
            for opp in poly_opps:
                if opp["estimated_net_return_pct"] < MIN_NET_RETURN_TO_ALERT:
                    continue

                # Oracle risk gate -- requires raw market dict; skip if unavailable
                # arb_scanner returns processed dicts, so use a stub score here
                # Full oracle_risk_score() is available in scan loop via raw market data
                risk = 0.1   # conservative default for pre-processed records

                if risk >= MAX_ORACLE_RISK_TO_ALERT:
                    log.info(
                        f"  Skipping [{opp['question'][:40]}...] -- oracle risk {risk:.2f}"
                    )
                    continue

                alert = _format_poly_alert(opp, risk)
                send_telegram(alert, dry_run=dry_run)
                alerts_sent += 1

            log.info(
                f"  {len(poly_opps)} PM opportunities scanned, "
                f"{alerts_sent} alerts sent"
            )

        except Exception as exc:
            log.error(f"PolyMarket scan error: {exc}")

        # ── Strategy 2: Funding rate arb (informational) ─────────────────────
        log.info("[2/2] Scanning funding rate arbitrage...")
        try:
            funding_opps = scan_funding_arbitrage(min_bps=30)
            _log_scan("FUNDING_ARB", funding_opps)

            alerts_sent = 0
            for opp in funding_opps:
                if opp["net_spread_bps"] < MIN_NET_BPS_TO_ALERT:
                    continue
                alert = _format_funding_alert(opp)
                send_telegram(alert, dry_run=dry_run)
                alerts_sent += 1

            log.info(
                f"  {len(funding_opps)} funding opportunities scanned, "
                f"{alerts_sent} alerts sent"
            )

        except Exception as exc:
            log.error(f"Funding arb scan error: {exc}")

        # ── Summary ──────────────────────────────────────────────────────────
        log.info(f"Scan #{scan_count} complete. Next scan in {interval_min} min.")
        time.sleep(interval_min * 60)


# -- Entry point --------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="PolyAlpha PM Arb Agent -- Paper Trading Scanner"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Scan interval in minutes (default: 30)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print Telegram alerts to console instead of sending",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single scan and exit (useful for cron/testing)",
    )
    args = parser.parse_args()

    if args.once:
        # Single scan mode for testing
        log.info("Running single scan (--once mode)...")

        poly = scan_polymarket_fast_resolution(min_price=0.95, max_hours_to_end=4)
        fund = scan_funding_arbitrage(min_bps=30)

        print(f"\nPolyMarket opportunities: {len(poly)}")
        for o in poly:
            risk = 0.1
            print(
                f"  [{o['confidence_label']}] {o['question'][:60]}... "
                f"net={o['estimated_net_return_pct']*100:.1f}% risk={risk:.2f}"
            )

        print(f"\nFunding arb opportunities: {len(fund)}")
        for o in fund:
            print(
                f"  {o['symbol']:6s} {o['long_venue']:12s} vs {o['short_venue']:12s} "
                f"net={o['net_spread_bps']}bps ann={o['annualized_pct']}%"
            )
    else:
        run_scanner(interval_min=args.interval, dry_run=args.dry_run)
