"""
viz_generator.py -- PolyAlpha Auto Visualization Engine

Generates 4 charts from history.jsonl and trade_history.jsonl.
Called by daily_runner.py after data collection.

Charts:
  1. Funding Rate Heatmap      (reports/funding_heatmap_{DATE}.html + .png)
  2. Arbitrage Opportunity Bar (reports/arb_opps_{DATE}.html + .png)
  3. Data Quality Timeline     (reports/data_quality_{DATE}.html + .png)
  4. Daily PnL Tracker         (reports/pnl_{DATE}.html + .png)

Usage:
  cd agent && python viz_generator.py
  cd agent && python viz_generator.py --date 2026-04-28
"""

import json
import argparse
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# -- Config -------------------------------------------------------------------
REPORTS_DIR       = Path(__file__).parent.parent / "reports"
HISTORY_FILE      = REPORTS_DIR / "history.jsonl"
TRADE_HISTORY_FILE = Path(__file__).parent / "logs" / "trade_history.jsonl"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("viz_generator")

REAL_COLOR  = "#22c55e"   # green-500
MOCK_COLOR  = "#f97316"   # orange-500
WARN_COLOR  = "#ef4444"   # red-500
BG_COLOR    = "#0f172a"   # dark background (matches dashboard theme)
TEXT_COLOR  = "#e2e8f0"


# -- Data loaders -------------------------------------------------------------

def _load_history() -> list[dict]:
    if not HISTORY_FILE.exists():
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


def _load_trade_history() -> list[dict]:
    if not TRADE_HISTORY_FILE.exists():
        return []
    records = []
    with open(TRADE_HISTORY_FILE) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return records


# -- Chart helpers ------------------------------------------------------------

def _dark_layout(**kwargs) -> dict:
    """Shared dark-mode layout config."""
    base = dict(
        plot_bgcolor=BG_COLOR,
        paper_bgcolor=BG_COLOR,
        font=dict(color=TEXT_COLOR, family="monospace"),
        margin=dict(l=60, r=40, t=60, b=60),
    )
    base.update(kwargs)
    return base


def _save(fig: go.Figure, name: str, date_str: str) -> tuple[Path, Path]:
    """Save chart as HTML and PNG. Returns (html_path, png_path)."""
    html_path = REPORTS_DIR / f"{name}_{date_str}.html"
    png_path  = REPORTS_DIR / f"{name}_{date_str}.png"
    fig.write_html(str(html_path))
    try:
        fig.write_image(str(png_path), width=1200, height=600, scale=2)
        log.info(f"  Saved: {png_path.name}")
    except Exception as exc:
        log.warning(f"  PNG export failed ({exc}) — HTML only saved")
        png_path = None
    log.info(f"  Saved: {html_path.name}")
    return html_path, png_path


# -- Chart 1: Funding Rate Heatmap --------------------------------------------

def chart_funding_heatmap(records: list[dict], date_str: str) -> tuple[Path, Path | None]:
    """
    Heatmap: X=date, Y=trading pair, Color=funding rate.
    Cells with source='mock' shown with red border marker.
    """
    rows = []
    for rec in records:
        date   = rec.get("date", rec.get("timestamp", "")[:10])
        src    = rec.get("funding_source", "mock")
        opps   = rec.get("funding", {}).get("data", [])
        for opp in opps:
            rows.append({
                "date":   date,
                "symbol": opp.get("symbol", "?"),
                "rate":   opp.get("net_spread_bps", 0),
                "source": src,
            })

    if not rows:
        log.warning("Chart 1: no data for heatmap")
        rows = [{"date": date_str, "symbol": "BTC", "rate": 0, "source": "mock"}]

    df = pd.DataFrame(rows)
    pivot = df.pivot_table(index="symbol", columns="date", values="rate", aggfunc="mean").fillna(0)

    fig = go.Figure(go.Heatmap(
        z=pivot.values.tolist(),
        x=list(pivot.columns),
        y=list(pivot.index),
        colorscale=[[0, "#1e293b"], [0.5, MOCK_COLOR], [1, REAL_COLOR]],
        colorbar=dict(title="Net bps", tickfont=dict(color=TEXT_COLOR)),
        hovertemplate="Date: %{x}<br>Pair: %{y}<br>Net bps: %{z}<extra></extra>",
    ))

    # Overlay red markers on mock-sourced dates
    mock_dates = df[df["source"] == "mock"]["date"].unique().tolist()
    for md in mock_dates:
        fig.add_vrect(
            x0=md, x1=md,
            fillcolor=WARN_COLOR, opacity=0.15,
            layer="below", line_width=2, line_color=WARN_COLOR,
            annotation_text="MOCK", annotation_position="top left",
            annotation_font_color=WARN_COLOR,
        )

    fig.update_layout(
        title=f"Funding Rate Heatmap (last {len(pivot.columns)} days)",
        xaxis_title="Date", yaxis_title="Trading Pair",
        **_dark_layout(),
    )
    return _save(fig, "funding_heatmap", date_str)


# -- Chart 2: Arbitrage Opportunity Bar Chart ---------------------------------

def chart_arb_opps(records: list[dict], date_str: str) -> tuple[Path, Path | None]:
    """
    Bar chart: X=opportunity ID, Y=net spread bps.
    Green if source=real, orange if source=mock.
    Title includes '⚠ MOCK DATA' if any mock present.
    """
    rows = []
    any_mock = False

    for rec in records:
        date = rec.get("date", rec.get("timestamp", "")[:10])
        for key, label in [("funding", "Funding"), ("polymarket", "PolyMarket")]:
            src  = rec.get(f"{key}_source", "mock")
            opps = rec.get(key, {}).get("data", [])
            if src == "mock":
                any_mock = True
            for opp in opps:
                value = opp.get("net_spread_bps") or opp.get("estimated_net_return_pct", 0) * 10_000
                name  = opp.get("symbol") or opp.get("question", "?")[:30]
                rows.append({"date": date, "name": f"[{label}] {name}", "value": value, "source": src})

    title = f"Arbitrage Opportunities — {date_str}"
    if any_mock:
        title += "  ⚠ MOCK DATA PRESENT"

    if not rows:
        rows = [{"date": date_str, "name": "No data", "value": 0, "source": "mock"}]

    df = pd.DataFrame(rows)
    latest = df[df["date"] == df["date"].max()]

    colors = [REAL_COLOR if s == "real" else MOCK_COLOR for s in latest["source"]]

    fig = go.Figure(go.Bar(
        x=latest["name"],
        y=latest["value"],
        marker_color=colors,
        text=[f"{v:.0f}bps" for v in latest["value"]],
        textposition="outside",
        hovertemplate="%{x}<br>%{y:.1f} bps<extra></extra>",
    ))
    fig.add_shape(type="line", x0=-0.5, x1=len(latest)-0.5, y0=50, y1=50,
                  line=dict(color=WARN_COLOR, width=1, dash="dash"))
    fig.add_annotation(x=len(latest)-0.5, y=50, text="50bps min threshold",
                       showarrow=False, font=dict(color=WARN_COLOR, size=10))
    fig.update_layout(
        title=title, xaxis_title="Opportunity", yaxis_title="Net Spread (bps)",
        **_dark_layout(),
    )
    return _save(fig, "arb_opps", date_str)


# -- Chart 3: Data Quality Timeline -------------------------------------------

def chart_data_quality(records: list[dict], date_str: str) -> tuple[Path, Path | None]:
    """
    Stacked bar: X=date, Y=count of real vs mock sources.
    Annotates dates with 100% mock.
    """
    rows = []
    for rec in records:
        date = rec.get("date", rec.get("timestamp", "")[:10])
        f_src = rec.get("funding_source", "mock")
        p_src = rec.get("polymarket_source", "mock")
        rows.append({
            "date":  date,
            "real":  sum([f_src == "real", p_src == "real"]),
            "mock":  sum([f_src == "mock",  p_src == "mock"]),
        })

    if not rows:
        rows = [{"date": date_str, "real": 0, "mock": 2}]

    df = pd.DataFrame(rows).groupby("date", as_index=False).mean()

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Real", x=df["date"], y=df["real"], marker_color=REAL_COLOR))
    fig.add_trace(go.Bar(name="Mock", x=df["date"], y=df["mock"], marker_color=MOCK_COLOR))

    # Annotate 100% mock dates
    full_mock = df[df["real"] == 0]["date"].tolist()
    for d in full_mock:
        fig.add_annotation(
            x=d, y=2.1, text="⚠", showarrow=False,
            font=dict(color=WARN_COLOR, size=18),
        )

    fig.update_layout(
        barmode="stack",
        title=f"Data Quality Timeline ({len(df)} days)",
        xaxis_title="Date", yaxis_title="Sources (max 2)",
        yaxis=dict(range=[0, 2.5]),
        legend=dict(font=dict(color=TEXT_COLOR)),
        **_dark_layout(),
    )
    return _save(fig, "data_quality", date_str)


# -- Chart 4: Daily PnL Tracker -----------------------------------------------

def chart_pnl(records: list[dict], date_str: str) -> tuple[Path, Path | None]:
    """
    Cumulative PnL line chart from trade_history.jsonl.
    Two lines: simulated (mock) vs live (real). Skips if no trade data.
    """
    trades = _load_trade_history()

    if not trades:
        log.info("Chart 4: no trade history — generating placeholder")
        fig = go.Figure()
        fig.add_annotation(
            x=0.5, y=0.5, text="No trade history yet.<br>Run agent.py to generate signals.",
            xref="paper", yref="paper", showarrow=False,
            font=dict(color=TEXT_COLOR, size=14),
        )
        fig.update_layout(title=f"Daily PnL Tracker — {date_str}", **_dark_layout())
        return _save(fig, "pnl", date_str)

    # Build cumulative PnL: won=True +1, won=False -1, won=None 0 (paper)
    sim_rows, live_rows = [], []
    for t in trades:
        ts  = t.get("ts", date_str)[:10]
        won = t.get("won")
        pnl = 1 if won is True else (-1 if won is False else 0)
        (live_rows if won is not None else sim_rows).append({"date": ts, "pnl": pnl})

    fig = go.Figure()

    for rows, label, color in [(sim_rows, "Simulated", MOCK_COLOR), (live_rows, "Live", REAL_COLOR)]:
        if not rows:
            continue
        df = pd.DataFrame(rows).groupby("date")["pnl"].sum().cumsum().reset_index()
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["pnl"],
            mode="lines+markers", name=label,
            line=dict(color=color, width=2),
        ))

    fig.add_shape(type="line", x0=0, x1=1, y0=0, y1=0,
                  xref="paper", line=dict(color=TEXT_COLOR, dash="dash", width=1))
    fig.update_layout(
        title=f"Daily PnL Tracker — {date_str}  ({len(trades)} signals)",
        xaxis_title="Date", yaxis_title="Cumulative PnL (signal units)",
        legend=dict(font=dict(color=TEXT_COLOR)),
        **_dark_layout(),
    )
    return _save(fig, "pnl", date_str)


# -- Main entry ---------------------------------------------------------------

def generate_all(date_str: str | None = None) -> dict[str, tuple]:
    """
    Generate all 4 charts. Returns dict of {chart_name: (html_path, png_path)}.
    Called by daily_runner.py and report_generator.py.
    """
    if date_str is None:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    records = _load_history()
    log.info(f"Loaded {len(records)} history records for charts")

    results = {}
    log.info("Generating Chart 1: Funding Rate Heatmap...")
    results["funding_heatmap"] = chart_funding_heatmap(records, date_str)

    log.info("Generating Chart 2: Arbitrage Opportunities...")
    results["arb_opps"] = chart_arb_opps(records, date_str)

    log.info("Generating Chart 3: Data Quality Timeline...")
    results["data_quality"] = chart_data_quality(records, date_str)

    log.info("Generating Chart 4: Daily PnL Tracker...")
    results["pnl"] = chart_pnl(records, date_str)

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PolyAlpha Visualization Engine")
    parser.add_argument("--date", default=None, help="Date string YYYY-MM-DD (default: today)")
    args = parser.parse_args()

    log.info(f"=== PolyAlpha Viz Generator [{args.date or 'today'}] ===")
    results = generate_all(args.date)

    print("\nCharts generated:")
    for name, (html, png) in results.items():
        png_status = png.name if png else "PNG FAILED"
        print(f"  {name}: {html.name} | {png_status}")
