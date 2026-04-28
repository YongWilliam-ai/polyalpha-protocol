"""
report_generator.py -- PolyAlpha HTML Daily Report + Telegram PNG Push

Assembles all 4 charts into a single daily HTML report and optionally
pushes PNG thumbnails to a Telegram channel.

Usage:
  cd agent && python report_generator.py
  cd agent && python report_generator.py --date 2026-04-28
  cd agent && python report_generator.py --no-telegram
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime, timezone
from pathlib import Path

import requests

try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")
except ImportError:
    pass

from viz_generator import generate_all

# -- Config -------------------------------------------------------------------
REPORTS_DIR        = Path(__file__).parent.parent / "reports"
HISTORY_FILE       = REPORTS_DIR / "history.jsonl"

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID", "")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("report_generator")


# -- Telegram helpers ---------------------------------------------------------

def _send_text(message: str) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log.warning("Telegram not configured")
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
        log.warning(f"Telegram text failed: {exc}")
        return False


def _send_photo(png_path: Path, caption: str = "") -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    if not png_path or not png_path.exists():
        log.warning(f"PNG not found: {png_path}")
        return False
    try:
        with open(png_path, "rb") as img:
            resp = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto",
                data={"chat_id": TELEGRAM_CHAT_ID, "caption": caption},
                files={"photo": img},
                timeout=15,
            )
        resp.raise_for_status()
        log.info(f"Sent photo: {png_path.name}")
        return True
    except Exception as exc:
        log.warning(f"Telegram photo failed ({png_path.name}): {exc}")
        return False


# -- Summary loader -----------------------------------------------------------

def _load_latest_summary(date_str: str) -> dict:
    path = REPORTS_DIR / f"summary_{date_str}.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {"funding_source": "unknown", "polymarket_source": "unknown",
            "opportunities_found": 0, "mock_percentage": 1.0}


# -- HTML report builder ------------------------------------------------------

def _badge(source: str) -> str:
    if source == "real":
        return '<span style="background:#22c55e;color:#000;padding:2px 8px;border-radius:4px;font-weight:bold">REAL DATA ✓</span>'
    return '<span style="background:#f97316;color:#000;padding:2px 8px;border-radius:4px;font-weight:bold">MOCK DATA ⚠</span>'


def build_html_report(date_str: str, chart_paths: dict, summary: dict) -> Path:
    """Assemble all 4 charts into a single daily HTML report."""

    def _embed(html_path: Path) -> str:
        """Read a Plotly HTML file and extract the inner div."""
        if not html_path or not html_path.exists():
            return "<p style='color:#f97316'>Chart not available</p>"
        content = html_path.read_text(encoding="utf-8")
        # Extract the body content (everything between <body> tags)
        start = content.find("<body>")
        end   = content.find("</body>")
        if start != -1 and end != -1:
            return content[start+6:end]
        return content  # fallback: embed full page

    funding_src = summary.get("funding_source", "unknown")
    poly_src    = summary.get("polymarket_source", "unknown")
    opps        = summary.get("opportunities_found", 0)
    mock_pct    = summary.get("mock_percentage", 1.0) * 100
    dq_score    = round((1 - summary.get("mock_percentage", 1.0)) * 100)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PolyAlpha Daily Report — {date_str}</title>
<style>
  body {{ background:#0f172a; color:#e2e8f0; font-family:monospace; margin:0; padding:24px; }}
  h1 {{ color:#818cf8; margin-bottom:4px; }}
  .subtitle {{ color:#64748b; margin-bottom:24px; font-size:0.9em; }}
  .badges {{ display:flex; gap:12px; margin-bottom:24px; flex-wrap:wrap; }}
  .card {{ background:#1e293b; border-radius:8px; padding:20px; margin-bottom:20px; }}
  .card h2 {{ color:#94a3b8; font-size:1em; margin:0 0 12px; }}
  .summary-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:12px; margin-bottom:24px; }}
  .metric {{ background:#1e293b; border-radius:8px; padding:16px; text-align:center; }}
  .metric .val {{ font-size:2em; font-weight:bold; color:#818cf8; }}
  .metric .label {{ color:#64748b; font-size:0.8em; margin-top:4px; }}
  table {{ width:100%; border-collapse:collapse; font-size:0.85em; }}
  th {{ color:#64748b; text-align:left; padding:6px 12px; border-bottom:1px solid #334155; }}
  td {{ padding:6px 12px; border-bottom:1px solid #1e293b; }}
</style>
</head>
<body>
<h1>PolyAlpha Daily Report</h1>
<div class="subtitle">Generated {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")} | Paper Trading Phase</div>

<div class="badges">
  <span>Funding: {_badge(funding_src)}</span>
  <span>PolyMarket: {_badge(poly_src)}</span>
</div>

<div class="summary-grid">
  <div class="metric"><div class="val">{opps}</div><div class="label">Opportunities Found</div></div>
  <div class="metric"><div class="val">{dq_score}</div><div class="label">Data Quality Score</div></div>
  <div class="metric"><div class="val">{mock_pct:.0f}%</div><div class="label">Mock Data %</div></div>
</div>

<div class="card">
  <h2>Summary Table</h2>
  <table>
    <tr><th>Metric</th><th>Value</th></tr>
    <tr><td>Date</td><td>{date_str}</td></tr>
    <tr><td>Funding Source</td><td>{funding_src.upper()}</td></tr>
    <tr><td>PolyMarket Source</td><td>{poly_src.upper()}</td></tr>
    <tr><td>Opportunities Found</td><td>{opps}</td></tr>
    <tr><td>Mock Percentage</td><td>{mock_pct:.1f}%</td></tr>
    <tr><td>Data Quality Score</td><td>{dq_score}/100</td></tr>
  </table>
</div>

<div class="card">
  <h2>Chart 1 — Funding Rate Heatmap</h2>
  {_embed(chart_paths.get("funding_heatmap", (None,))[0])}
</div>

<div class="card">
  <h2>Chart 2 — Arbitrage Opportunities</h2>
  {_embed(chart_paths.get("arb_opps", (None,))[0])}
</div>

<div class="card">
  <h2>Chart 3 — Data Quality Timeline</h2>
  {_embed(chart_paths.get("data_quality", (None,))[0])}
</div>

<div class="card">
  <h2>Chart 4 — Daily PnL Tracker</h2>
  {_embed(chart_paths.get("pnl", (None,))[0])}
</div>

</body>
</html>"""

    report_path = REPORTS_DIR / f"daily_report_{date_str}.html"
    report_path.write_text(html, encoding="utf-8")
    log.info(f"HTML report: {report_path}")
    return report_path


# -- Telegram push ------------------------------------------------------------

def push_to_telegram(chart_paths: dict, summary: dict, date_str: str) -> None:
    """Send 4 PNG charts + text summary to Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log.warning("Telegram not configured -- skipping push")
        return

    funding_src = summary.get("funding_source", "?")
    poly_src    = summary.get("polymarket_source", "?")
    opps        = summary.get("opportunities_found", 0)
    dq_score    = round((1 - summary.get("mock_percentage", 1.0)) * 100)

    # Text summary first
    text = (
        f"*PolyAlpha Daily* -- {date_str}\n"
        f"Funding: `{funding_src.upper()}` | PolyMarket: `{poly_src.upper()}`\n"
        f"Opportunities found: {opps}\n"
        f"Data quality score: {dq_score}/100"
    )
    _send_text(text)

    # Send each PNG
    captions = {
        "funding_heatmap": "Chart 1 — Funding Rate Heatmap",
        "arb_opps":        "Chart 2 — Arbitrage Opportunities",
        "data_quality":    "Chart 3 — Data Quality Timeline",
        "pnl":             "Chart 4 — Daily PnL Tracker",
    }
    for key, caption in captions.items():
        paths = chart_paths.get(key, (None, None))
        png   = paths[1] if paths else None
        _send_photo(png, caption=caption)


# -- Main ---------------------------------------------------------------------

def run(date_str: str | None = None, send_telegram: bool = True) -> Path:
    if date_str is None:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    log.info(f"=== PolyAlpha Report Generator [{date_str}] ===")

    # Generate all charts
    chart_paths = generate_all(date_str)

    # Load summary
    summary = _load_latest_summary(date_str)

    # Build HTML report
    report_path = build_html_report(date_str, chart_paths, summary)

    # Telegram push
    if send_telegram:
        push_to_telegram(chart_paths, summary, date_str)

    log.info(f"Report ready: {report_path}")
    return report_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PolyAlpha Report Generator")
    parser.add_argument("--date", default=None, help="Date YYYY-MM-DD (default: today)")
    parser.add_argument("--no-telegram", action="store_true", help="Skip Telegram push")
    args = parser.parse_args()

    path = run(date_str=args.date, send_telegram=not args.no_telegram)
    print(f"\nReport: {path}")
