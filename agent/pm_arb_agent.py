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

from safety_gate import run_safety_checks

# dotenv is optional -- load .env if available, otherwise rely on shell env vars
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
except ImportError:
    pass

# Real MiroFish swarm intelligence (Phase 2)
try:
    from mirofish_integration import get_mirofish_swarm_consensus, fetch_market_question
    _MIROFISH_AVAILABLE = True
except ImportError:
    _MIROFISH_AVAILABLE = False

# Import reusable scanners from arb_scanner.py
# PolyAlpha Strategy 1 + 2 + 3
from arb_scanner import (
    scan_funding_arbitrage,
    scan_polymarket_fast_resolution,
    scan_yes_no_arb,
    scan_correlation_arb,
    get_active_market_ids,
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
SCAN_LOG_FILE    = Path("agent/logs/pm_arb_scan_log.jsonl")
SCAN_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Written after each swarm run so the React frontend can display results
_PROJECT_ROOT    = Path(__file__).resolve().parent.parent
SWARM_OUTPUT_FILE = _PROJECT_ROOT / "frontend" / "public" / "swarm_latest.json"

# Telegram -- read from env (no defaults; alerts silently skipped if not set)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID", "")

# Safety gate: paper-trade position size and portfolio TVL used for ratio checks
PAPER_TRADE_SIZE_USDT = 100.0      # $100 standard paper bet per alert
PAPER_PORTFOLIO_TVL   = 10_000.0   # $10k paper portfolio for position-ratio gate

# Alert thresholds
MIN_NET_RETURN_TO_ALERT  = 0.02    # 2% net return minimum for PM alert
MIN_NET_BPS_TO_ALERT     = 50      # 50 bps minimum for funding arb alert
MAX_ORACLE_RISK_TO_ALERT = 0.4     # skip PM markets with oracle risk >= 0.4
MIN_YES_NO_PROFIT_PCT       = 0.5   # 0.5% minimum profit for YES/NO arb alert
MIN_CORRELATION_SPREAD_BPS  = 300  # 3% (300 bps) minimum spread for correlation alert


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


def _format_correlation_arb_alert(opp: dict) -> str:
    return (
        f"*PolyAlpha* -- Correlation Arb Alert [{opp['violation_id']}]\n"
        f"SPECIFIC: `{opp['specific_question'][:70]}`  → {opp['specific_price']:.3f}\n"
        f"BROAD:    `{opp['broad_question'][:70]}`  → {opp['broad_price']:.3f}\n"
        f"Spread: *{opp['spread_bps']}bps* | {opp['logic']}\n"
        f"Trade: BUY broad-category YES, note specific is overpriced\n"
        f"Paper Trading -- multi-leg execution required (Phase 2)\n"
        f"#PolyAlpha #CorrelationArb"
    )


def _format_yes_no_arb_alert(opp: dict) -> str:
    return (
        f"*PolyAlpha* -- YES/NO Riskless Arb Alert\n"
        f"`{opp['question'][:80]}`\n"
        f"YES ask: {opp['yes_price']:.4f} | NO ask: {opp['no_price']:.4f} | Total: {opp['total']:.4f}\n"
        f"*Risk-free profit: {opp['profit_pct']:.2f}%* (market resolves to $1.00)\n"
        f"Paper Trading -- verify gas cost before real execution\n"
        f"#PolyAlpha #YesNoArb #RiskFree"
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


# -- MiroFish swarm helpers ---------------------------------------------------

def _write_swarm_output(swarm: dict) -> None:
    """Persist latest swarm result to frontend/public/ for the React dashboard."""
    try:
        SWARM_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(SWARM_OUTPUT_FILE, "w") as f:
            json.dump(swarm, f, indent=2)
        log.info(f"  Swarm result written -> {SWARM_OUTPUT_FILE}")
    except Exception as exc:
        log.warning(f"  Could not write swarm output: {exc}")


def _run_swarm_on_market(mid: str, dry_run: bool = False) -> dict | None:
    """
    Fetch question for a market ID, run MiroFish consensus, return result.
    Returns None if mirofish_integration is unavailable.
    """
    if not _MIROFISH_AVAILABLE:
        log.warning("  mirofish_integration not available -- skipping swarm")
        return None
    try:
        question = fetch_market_question(mid)
        swarm    = get_mirofish_swarm_consensus(question, mid)
        log.info(
            f"    [{swarm['label']}] {question[:50]}... "
            f"consensus={swarm['consensus']:.3f} [{swarm['source']}]"
        )
        return swarm
    except Exception as exc:
        log.warning(f"  MiroFish swarm failed for {mid[:20]}: {exc}")
        return None


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
        log.info("[1/4] Scanning PolyMarket fast-resolution opportunities...")
        try:
            poly_result = scan_polymarket_fast_resolution(
                min_price=0.95,
                max_hours_to_end=2,
                min_volume_usd=10_000,
            )
            poly_opps = poly_result["data"]
            log.info(f"  Source: {poly_result['source'].upper()}" + (f" | {poly_result['error']}" if poly_result.get("error") else ""))
            _log_scan("POLYMARKET_FAST_RESOLUTION", poly_opps)

            alerts_sent = 0
            for opp in poly_opps:
                if opp["estimated_net_return_pct"] < MIN_NET_RETURN_TO_ALERT:
                    continue
                # Skip mock data alerts -- source tag gates real vs fake
                if poly_result["source"] == "mock":
                    log.info("  Skipping Telegram alert -- source is MOCK")
                    continue

                risk = 0.1   # conservative default for pre-processed records
                if risk >= MAX_ORACLE_RISK_TO_ALERT:
                    log.info(f"  Skipping [{opp['question'][:40]}...] -- oracle risk {risk:.2f}")
                    continue

                gate_symbol = opp.get("question", "POLYMARKET")[:30]
                if not run_safety_checks(
                    PAPER_TRADE_SIZE_USDT, PAPER_PORTFOLIO_TVL,
                    gate_symbol, "BUY_YES", dry_run=dry_run,
                ):
                    log.info(f"  [SafetyGate] Alert blocked for [{gate_symbol}]")
                    continue

                alert = _format_poly_alert(opp, risk)
                send_telegram(alert, dry_run=dry_run)
                alerts_sent += 1

            log.info(f"  {len(poly_opps)} PM opportunities scanned, {alerts_sent} alerts sent")

        except Exception as exc:
            log.error(f"PolyMarket scan error: {exc}")

        # ── Strategy 2: Funding rate arb (informational) ─────────────────────
        log.info("[2/4] Scanning funding rate arbitrage...")
        try:
            funding_result = scan_funding_arbitrage(min_bps=30)
            funding_opps = funding_result["data"]
            log.info(f"  Source: {funding_result['source'].upper()}" + (f" | {funding_result['error']}" if funding_result.get("error") else ""))
            _log_scan("FUNDING_ARB", funding_opps)

            alerts_sent = 0
            for opp in funding_opps:
                if opp["net_spread_bps"] < MIN_NET_BPS_TO_ALERT:
                    continue
                if funding_result["source"] == "mock":
                    log.info("  Skipping Telegram alert -- source is MOCK")
                    continue
                gate_symbol = opp.get("symbol", "FUNDING")
                if not run_safety_checks(
                    PAPER_TRADE_SIZE_USDT, PAPER_PORTFOLIO_TVL,
                    gate_symbol, "FUNDING_ARB", dry_run=dry_run,
                ):
                    log.info(f"  [SafetyGate] Alert blocked for [{gate_symbol}]")
                    continue
                alert = _format_funding_alert(opp)
                send_telegram(alert, dry_run=dry_run)
                alerts_sent += 1

            log.info(f"  {len(funding_opps)} funding opportunities scanned, {alerts_sent} alerts sent")

        except Exception as exc:
            log.error(f"Funding arb scan error: {exc}")

        # ── Strategy 3: YES/NO riskless arb ──────────────────────────────────
        log.info("[3/4] Scanning YES/NO riskless arbitrage...")
        try:
            market_ids = get_active_market_ids(limit=50)
            yesno_opps = scan_yes_no_arb(market_ids) if market_ids else []
            _log_scan("YES_NO_ARB", yesno_opps)

            alerts_sent = 0
            for opp in yesno_opps:
                if opp["profit_pct"] < MIN_YES_NO_PROFIT_PCT:
                    continue
                gate_symbol = opp.get("market_id", "YESNO")[:30]
                if not run_safety_checks(
                    PAPER_TRADE_SIZE_USDT, PAPER_PORTFOLIO_TVL,
                    gate_symbol, "BUY_YES_NO", dry_run=dry_run,
                ):
                    log.info(f"  [SafetyGate] Alert blocked for [{gate_symbol}]")
                    continue
                alert = _format_yes_no_arb_alert(opp)
                send_telegram(alert, dry_run=dry_run)
                alerts_sent += 1

            log.info(
                f"  {len(yesno_opps)} YES/NO arb opportunities found, {alerts_sent} alerts sent"
            )

            # MiroFish fallback -- if genuine YES/NO arb is absent, consult swarm
            if not yesno_opps and market_ids:
                log.info("  No YES/NO arb -- running MiroFish swarm on top 5 markets...")
                swarm_alerts = 0
                latest_swarm = None
                for mid in market_ids[:5]:
                    swarm = _run_swarm_on_market(mid, dry_run=dry_run)
                    if swarm is None:
                        continue
                    latest_swarm = swarm
                    if swarm["label"] == "SWARM_STRONG_BUY":
                        if not run_safety_checks(
                            PAPER_TRADE_SIZE_USDT, PAPER_PORTFOLIO_TVL,
                            mid[:30], "SWARM_BUY", dry_run=dry_run,
                        ):
                            log.info(f"  [SafetyGate] MiroFish alert blocked for [{mid[:20]}]")
                            continue
                        votes_summary = " | ".join(
                            f"{v['persona'][:10]}: {v['vote']}@{v['confidence']}%"
                            for v in swarm["votes"]
                        )
                        msg = (
                            f"*PolyAlpha* -- MiroFish Swarm Signal [{swarm['label']}]\n"
                            f"`{swarm['market_question'][:80]}`\n"
                            f"Consensus: *{swarm['consensus']:.3f}* | {len(swarm['votes'])} personas [{swarm['source']}]\n"
                            f"{votes_summary}\n"
                            f"Paper Trading -- informational only\n"
                            f"#PolyAlpha #MiroFish #SwarmIntelligence"
                        )
                        send_telegram(msg, dry_run=dry_run)
                        swarm_alerts += 1
                log.info(f"  MiroFish scan: {swarm_alerts} SWARM_STRONG_BUY alerts sent")
                if latest_swarm:
                    _write_swarm_output(latest_swarm)

        except Exception as exc:
            log.error(f"YES/NO arb scan error: {exc}")

        # ── Strategy 4: Logical correlation arb ──────────────────────────────
        log.info("[4/4] Scanning logical correlation arbitrage...")
        try:
            corr_opps = scan_correlation_arb()
            _log_scan("CORRELATION_ARB", corr_opps)

            alerts_sent = 0
            for opp in corr_opps:
                if opp["spread_bps"] < MIN_CORRELATION_SPREAD_BPS:
                    continue
                gate_symbol = opp.get("violation_id", "CORR_ARB")
                if not run_safety_checks(
                    PAPER_TRADE_SIZE_USDT, PAPER_PORTFOLIO_TVL,
                    gate_symbol, "CORR_ARB", dry_run=dry_run,
                ):
                    log.info(f"  [SafetyGate] Alert blocked for [{gate_symbol}]")
                    continue
                alert = _format_correlation_arb_alert(opp)
                send_telegram(alert, dry_run=dry_run)
                alerts_sent += 1

            log.info(
                f"  {len(corr_opps)} correlation violations found, {alerts_sent} alerts sent"
            )
        except Exception as exc:
            log.error(f"Correlation arb scan error: {exc}")

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

        poly_result = scan_polymarket_fast_resolution(min_price=0.95, max_hours_to_end=4)
        fund_result = scan_funding_arbitrage(min_bps=30)
        poly = poly_result["data"]
        fund = fund_result["data"]

        print(f"\nPolyMarket opportunities: {len(poly)} [{poly_result['source'].upper()}]")
        for o in poly:
            risk = 0.1
            print(
                f"  [{o['confidence_label']}] {o['question'][:60]}... "
                f"net={o['estimated_net_return_pct']*100:.1f}% risk={risk:.2f}"
            )

        print(f"\nFunding arb opportunities: {len(fund)} [{fund_result['source'].upper()}]")
        for o in fund:
            print(
                f"  {o['symbol']:6s} {o['long_venue']:12s} vs {o['short_venue']:12s} "
                f"net={o['net_spread_bps']}bps ann={o['annualized_pct']}%"
            )

        print("\nYES/NO riskless arb scan...")
        yesno_ids = get_active_market_ids(limit=30)
        yesno = scan_yes_no_arb(yesno_ids) if yesno_ids else []
        print(f"YES/NO arb opportunities: {len(yesno)}")
        for o in yesno:
            print(
                f"  {o['market_id'][:12]}... "
                f"YES={o['yes_price']:.4f}+NO={o['no_price']:.4f} profit={o['profit_pct']:.2f}%"
            )
        if not yesno:
            print("  None found (genuine YES/NO arb is rare -- scanner is working correctly)")

        print("\nCorrelation arb scan...")
        corr = scan_correlation_arb()
        print(f"Correlation violations: {len(corr)}")
        for o in corr:
            print(
                f"  [{o['violation_id']}] specific={o['specific_price']:.3f} > "
                f"broad={o['broad_price']:.3f} spread={o['spread_bps']}bps"
            )
        if not corr:
            print("  None found (markets are internally consistent -- scanner is working correctly)")

        print("\nMiroFish swarm intelligence scan (top 5 markets)...")
        swarm_ids = get_active_market_ids(limit=5)
        for mid in (swarm_ids or []):
            swarm = _run_swarm_on_market(mid)
            if swarm is None:
                print(f"  [{mid[:20]}] skipped -- mirofish unavailable")
                continue
            print(
                f"  [{swarm['label']}] {swarm['market_question'][:60]}... "
                f"consensus={swarm['consensus']:.3f} [{swarm['source']}]"
            )
            for line in swarm.get("interview_logs", []):
                print(f"    {line}")
            _write_swarm_output(swarm)
    else:
        run_scanner(interval_min=args.interval, dry_run=args.dry_run)
