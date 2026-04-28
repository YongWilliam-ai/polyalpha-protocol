"""
arb_scanner.py -- PolyAlpha Arbitrage Scanner (Paper Trading Mode)

Two scanners:
  scan_funding_arbitrage()         -- cross-venue funding rate spread (9 exchanges)
  scan_polymarket_fast_resolution() -- near-settlement PolyMarket arb

Paper Trading phase: read-only. NO trade execution, NO private keys.

References:
  @hunterweb303 funding-rates-mcp: https://github.com/duolaAmengweb3/funding-arb-scanner
  PolyAlpha Strategy 1: PolyMarket fast-resolution arb (Opus evaluation, April 2026)
"""

import os
import json
import time
import requests
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

# -- Constants -----------------------------------------------------------------

TAKER_FEE_PER_LEG_BPS = 5   # 0.05% per leg; 10bps round-trip
ROUND_TRIP_FEE_BPS    = TAKER_FEE_PER_LEG_BPS * 2

# @hunterweb303 funding-rates-mcp — public API endpoints (no auth required)
HL_INFO_URL    = "https://api.hyperliquid.xyz/info"
BINANCE_FR_URL = "https://fapi.binance.com/fapi/v1/fundingRate"
# OKX V5 per-instrument endpoint — instType=SWAP is NOT a valid param here
# Reference: https://www.okx.com/docs-v5/en/#public-data-rest-api-get-funding-rate
OKX_FR_URL     = "https://www.okx.com/api/v5/public/funding-rate"
OKX_TARGET_INSTS = [
    "BTC-USDT-SWAP", "ETH-USDT-SWAP", "SOL-USDT-SWAP",
    "MATIC-USDT-SWAP", "DOGE-USDT-SWAP", "XRP-USDT-SWAP",
]

# PolyAlpha Strategy 1 — PolyMarket API endpoints
GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API  = "https://clob.polymarket.com"

# Error log — written on API failures (never raised to stdout)
ERROR_LOG = Path("agent/logs/error.log")


# -- Mock fallback data --------------------------------------------------------

MOCK_FUNDING_OPPORTUNITIES = [
    {
        "symbol": "BTC",
        "long_venue": "Paradex",
        "short_venue": "Hyperliquid",
        "gross_spread_bps": 115,
        "net_spread_bps": 95,
        "annualized_pct": 3.47,
        "estimated_8h_pnl_per_10k": 0.95,
    },
    {
        "symbol": "ETH",
        "long_venue": "Drift",
        "short_venue": "Binance",
        "gross_spread_bps": 88,
        "net_spread_bps": 68,
        "annualized_pct": 2.48,
        "estimated_8h_pnl_per_10k": 0.68,
    },
    {
        "symbol": "SOL",
        "long_venue": "OKX",
        "short_venue": "Hyperliquid",
        "gross_spread_bps": 62,
        "net_spread_bps": 42,
        "annualized_pct": 1.53,
        "estimated_8h_pnl_per_10k": 0.42,
    },
]

MOCK_POLYMARKET_OPPORTUNITIES = [
    {
        "market_id": "MOCK-0x1234",
        "question": "[MOCK] Will BTC close above $90,000 today?",
        "end_time": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
        "yes_price": 0.96,
        "no_price": 0.04,
        "volume_24h": 125000,
        "estimated_net_return_pct": 0.035,
        "confidence_label": "HIGH",
    },
]


# -- Funding Rate Arbitrage Scanner --------------------------------------------

def _fetch_hl_funding_rates() -> dict[str, float]:
    """
    Fetch current funding rates from Hyperliquid.
    # @hunterweb303 funding-rates-mcp -- HL public endpoint
    Returns {symbol: funding_rate_per_8h} e.g. {"BTC": 0.0001, "ETH": -0.00005}
    """
    resp = requests.post(
        HL_INFO_URL,
        json={"type": "metaAndAssetCtxs"},
        timeout=5,
    )
    resp.raise_for_status()
    data = resp.json()

    meta     = data[0].get("universe", [])
    contexts = data[1]

    rates = {}
    for asset_meta, ctx in zip(meta, contexts):
        symbol = asset_meta.get("name", "")
        fr_str = ctx.get("funding", "0")
        try:
            rates[symbol] = float(fr_str)
        except (ValueError, TypeError):
            pass
    return rates


def _fetch_binance_funding_rates() -> dict[str, float]:
    """
    Fetch current funding rates from Binance USDT-M perps.
    # @hunterweb303 funding-rates-mcp -- Binance public endpoint
    Returns {symbol: funding_rate_per_8h}
    """
    resp = requests.get(BINANCE_FR_URL, timeout=5)
    resp.raise_for_status()
    items = resp.json()

    rates = {}
    for item in items:
        raw = item.get("symbol", "")
        # Strip USDT suffix to normalize: BTCUSDT -> BTC
        symbol = raw.replace("USDT", "").replace("USD", "")
        try:
            rates[symbol] = float(item.get("fundingRate", 0))
        except (ValueError, TypeError):
            pass
    return rates


def _fetch_okx_funding_rates() -> dict[str, float]:
    """
    Fetch funding rates from OKX V5 API, one request per target instrument.
    # @hunterweb303 funding-rates-mcp -- OKX V5 per-instrument endpoint
    # GET /api/v5/public/funding-rate?instId=BTC-USDT-SWAP
    # instType=SWAP is NOT a valid query param on this endpoint (causes HTTP 400)

    Retry policy: 3 attempts per instrument, exponential backoff (1s, 2s).
    If ALL instruments fail after retries: raises RuntimeError and logs to error.log.
    Partial failures (some instruments fail) are logged as warnings and skipped.

    Returns {symbol: funding_rate_per_8h}  e.g. {"BTC": 0.0001, "ETH": -0.00005}
    """
    rates: dict[str, float] = {}
    partial_failures: list[tuple[str, Exception]] = []

    for inst_id in OKX_TARGET_INSTS:
        symbol = inst_id.split("-")[0]  # "BTC-USDT-SWAP" -> "BTC"
        last_exc: Optional[Exception] = None

        for attempt in range(3):
            try:
                resp = requests.get(
                    OKX_FR_URL,
                    params={"instId": inst_id},
                    timeout=5,
                )
                resp.raise_for_status()
                payload = resp.json()
                if payload.get("code") != "0":
                    raise ValueError(
                        f"OKX API error code={payload.get('code')} msg={payload.get('msg')}"
                    )
                data = payload.get("data", [])
                if data:
                    rates[symbol] = float(data[0].get("fundingRate", 0))
                last_exc = None
                break
            except Exception as exc:
                last_exc = exc
                if attempt < 2:
                    time.sleep(2 ** attempt)  # 1 s after attempt 0, 2 s after attempt 1

        if last_exc is not None:
            partial_failures.append((inst_id, last_exc))

    if partial_failures:
        _write_error_log(
            f"OKX partial/full failure — {len(partial_failures)}/{len(OKX_TARGET_INSTS)} "
            f"instruments failed: {[(i, str(e)) for i, e in partial_failures]}"
        )

    if not rates:
        raise RuntimeError(
            f"OKX API unavailable after 3 retries for all {len(OKX_TARGET_INSTS)} "
            f"instruments. First error: {partial_failures[0][1]}"
        )

    return rates


def _write_error_log(message: str) -> None:
    """Append timestamped error to agent/logs/error.log."""
    try:
        ERROR_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(ERROR_LOG, "a") as f:
            f.write(f"[{datetime.now(timezone.utc).isoformat()}] {message}\n")
    except Exception:
        pass  # never let logging crash the scanner


def scan_funding_arbitrage(min_bps: int = 50) -> dict:
    """
    Scans 9 exchanges for funding rate arbitrage opportunities.
    Returns top 3 pairs with highest net spread (after taker fees).

    # @hunterweb303 funding-rates-mcp conceptual wrapper
    Data sources: Hyperliquid, Binance, OKX (live) + Bybit/dYdX/Drift/Vertex/Paradex/Aevo (stub)

    Returns:
        {
          "data": [{symbol, long_venue, short_venue, gross_spread_bps,
                    net_spread_bps, annualized_pct, estimated_8h_pnl_per_10k}],
          "source": "real" | "mock",
          "timestamp": "ISO8601",
          "error": null | "error description if mock was used"
        }
    """
    ts = datetime.now(timezone.utc).isoformat()
    print(f"[{ts}] Fetching funding rates from HL / Binance / OKX...")

    venue_rates: dict[str, dict[str, float]] = {}

    try:
        venue_rates["Hyperliquid"] = _fetch_hl_funding_rates()
        print(f"  HL: {len(venue_rates['Hyperliquid'])} symbols")
    except Exception as exc:
        print(f"  HL fetch failed: {exc} -- skipping")

    try:
        venue_rates["Binance"] = _fetch_binance_funding_rates()
        print(f"  Binance: {len(venue_rates['Binance'])} symbols")
    except Exception as exc:
        print(f"  Binance fetch failed: {exc} -- skipping")

    try:
        venue_rates["OKX"] = _fetch_okx_funding_rates()
        print(f"  OKX: {len(venue_rates['OKX'])} symbols")
    except Exception as exc:
        print(f"  OKX fetch failed: {exc} -- skipping")

    if not venue_rates:
        err = "All live funding rate APIs failed (HL, Binance, OKX)"
        _write_error_log(err)
        print(f"  {err} -- using mock data")
        return {"data": MOCK_FUNDING_OPPORTUNITIES[:3], "source": "mock", "timestamp": ts, "error": err}

    # Build cross-venue spread for each symbol present in >= 2 venues
    all_symbols = set()
    for rates in venue_rates.values():
        all_symbols.update(rates.keys())

    opportunities = []
    target_symbols = {"BTC", "ETH", "SOL", "ARB", "OP", "MATIC", "AVAX", "DOGE", "XRP"}

    for symbol in all_symbols & target_symbols:
        present = {
            venue: rates[symbol]
            for venue, rates in venue_rates.items()
            if symbol in rates
        }
        if len(present) < 2:
            continue

        max_venue = max(present, key=present.get)
        min_venue = min(present, key=present.get)
        max_rate  = present[max_venue]
        min_rate  = present[min_venue]

        # Gross spread in bps (per 8h funding period)
        gross_spread_bps = int((max_rate - min_rate) * 10_000)
        net_spread_bps   = gross_spread_bps - ROUND_TRIP_FEE_BPS

        if net_spread_bps < min_bps:
            continue

        # 3 funding periods/day * 365 days
        annualized_pct = round(net_spread_bps / 10_000 * 3 * 365 * 100, 2)
        # Estimated 8h PnL per $10k notional
        estimated_8h_pnl_per_10k = round(net_spread_bps / 10_000 * 10_000, 2)

        opp = {
            "symbol":                   symbol,
            "long_venue":               min_venue,   # go long where rate is low (pay less)
            "short_venue":              max_venue,   # go short where rate is high (collect more)
            "gross_spread_bps":         gross_spread_bps,
            "net_spread_bps":           net_spread_bps,
            "annualized_pct":           annualized_pct,
            "estimated_8h_pnl_per_10k": estimated_8h_pnl_per_10k,
        }
        opportunities.append(opp)
        print(
            f"  [{symbol}] {min_venue} vs {max_venue}: "
            f"gross={gross_spread_bps}bps net={net_spread_bps}bps ann={annualized_pct}%"
        )

    if not opportunities:
        err = f"No live pairs above {min_bps}bps net spread -- using mock data"
        print(f"  {err}")
        return {"data": MOCK_FUNDING_OPPORTUNITIES[:3], "source": "mock", "timestamp": ts, "error": err}

    opportunities.sort(key=lambda x: x["net_spread_bps"], reverse=True)
    top3 = opportunities[:3]
    print(f"  Top {len(top3)} funding arb opportunities found (live data)")
    return {"data": top3, "source": "real", "timestamp": ts, "error": None}


# -- PolyMarket Fast-Resolution Scanner ----------------------------------------

def _parse_end_time(market: dict) -> Optional[datetime]:
    """Parse endDateIso or endDate field into a timezone-aware datetime."""
    for key in ("endDateIso", "endDate", "end_date_iso"):
        raw = market.get(key)
        if not raw:
            continue
        try:
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except (ValueError, TypeError):
            continue
    return None


def scan_polymarket_fast_resolution(
    min_price: float = 0.95,
    max_hours_to_end: int = 2,
    min_volume_usd: float = 10000,
) -> dict:
    """
    Scans PolyMarket CLOB for markets near settlement with high-certainty pricing.

    # PolyAlpha Strategy 1: fast-resolution arb
    Strategy logic: If a market's YES price > 0.95 AND it resolves in <2 hours,
    buying YES at 0.96 captures a ~4% spread assuming correct resolution.

    # WARNING: Resolution oracle delay risk -- verify event has actually concluded
    # IRL before entering. UMA Optimistic Oracle has a 48h dispute window.
    # A disputed resolution locks capital and can result in a loss.

    APIs:
      Gamma API: https://gamma-api.polymarket.com/markets
      CLOB API:  https://clob.polymarket.com/markets (order book)

    Returns:
        {
          "data": [{market_id, question, end_time, yes_price, no_price,
                    volume_24h, estimated_net_return_pct, confidence_label}],
          "source": "real" | "mock",
          "timestamp": "ISO8601",
          "error": null | "error description if mock was used"
        }
    """
    ts  = datetime.now(timezone.utc).isoformat()
    now = datetime.now(timezone.utc)
    cutoff = now + timedelta(hours=max_hours_to_end)

    print(f"[{ts}] Scanning PolyMarket near-settlement (end < {cutoff.strftime('%H:%M UTC')})...")

    try:
        resp = requests.get(
            f"{GAMMA_API}/markets",
            params={"active": "true", "limit": 100},
            timeout=5,
        )
        resp.raise_for_status()
        markets = resp.json()
    except Exception as exc:
        err = f"Gamma API unavailable: {exc}"
        _write_error_log(err)
        print(f"  {err} -- using mock data")
        return {"data": MOCK_POLYMARKET_OPPORTUNITIES, "source": "mock", "timestamp": ts, "error": err}

    qualifying = []

    for m in markets:
        end_dt = _parse_end_time(m)
        if end_dt is None or end_dt > cutoff or end_dt < now:
            continue

        # Extract volume
        try:
            volume_24h = float(m.get("volume24hr", m.get("volume", 0)) or 0)
        except (ValueError, TypeError):
            volume_24h = 0

        if volume_24h < min_volume_usd:
            continue

        # Extract YES price (best ask = cheapest offer for YES token)
        try:
            outcome_prices = m.get("outcomePrices", [])
            yes_price = float(outcome_prices[0]) if outcome_prices else float(m.get("bestBid", 0))
            no_price  = float(outcome_prices[1]) if len(outcome_prices) > 1 else 1 - yes_price
        except (ValueError, TypeError, IndexError):
            continue

        # Filter: YES must be priced > min_price OR NO must be priced > min_price
        entry_price = None
        if yes_price >= min_price:
            entry_price = yes_price
        elif no_price >= min_price:
            entry_price = no_price
            yes_price, no_price = no_price, yes_price  # swap so yes_price = the high side

        if entry_price is None:
            continue

        # PolyAlpha Strategy 1: net return calculation
        estimated_gross_return    = round(1.0 - entry_price, 4)
        estimated_gas_fee_pct     = 0.005   # 0.5% Polygon gas estimate
        estimated_net_return_pct  = round(estimated_gross_return - estimated_gas_fee_pct, 4)

        confidence_label = (
            "HIGH" if volume_24h > 50_000 and entry_price > 0.97 else "MEDIUM"
        )

        opp = {
            "market_id":               m.get("conditionId", m.get("id", "unknown")),
            "question":                m.get("question", "")[:120],
            "end_time":                end_dt.isoformat(),
            "yes_price":               round(entry_price, 4),
            "no_price":                round(1 - entry_price, 4),
            "volume_24h":              volume_24h,
            "estimated_net_return_pct": estimated_net_return_pct,
            "confidence_label":        confidence_label,
        }
        qualifying.append(opp)

        print(
            f"  [{confidence_label}] {opp['question'][:60]}... | "
            f"price={entry_price:.3f} net={estimated_net_return_pct*100:.1f}% "
            f"ends={end_dt.strftime('%H:%M UTC')}"
        )

    if not qualifying:
        print("  No qualifying markets found (may be off-hours or API filtered)")

    qualifying.sort(key=lambda x: x["estimated_net_return_pct"], reverse=True)
    return {"data": qualifying, "source": "real", "timestamp": ts, "error": None}


# -- Oracle Risk Scorer -------------------------------------------------------

# Resolution source strings that indicate high dispute risk
_HIGH_RISK_RESOLUTION_SOURCES = {"uma", "optimistic oracle", "uma optimistic"}
_CONTINGENT_KEYWORDS = (
    "contingent", "unless", "disputed", "var", "review", "appeal", "challenge",
    "recount", "certification", "ratified",
)


def oracle_risk_score(market: dict) -> float:
    """
    Heuristic UMA dispute probability score for a PolyMarket market.
    Returns 0.0 (safe) to 1.0 (high dispute risk).

    # PolyAlpha Strategy 1: oracle risk filter
    # UMA Optimistic Oracle has a 48h dispute window. A disputed resolution
    # locks capital with potential full loss. This scorer helps skip risky markets.

    Inputs examined:
      - resolutionSource: UMA/Optimistic Oracle -> elevated base risk
      - question text: contingent language -> elevated risk
      - volume: thin liquidity often signals disagreement among participants
    """
    score = 0.0

    # Resolution source check
    resolution_src = str(market.get("resolutionSource", "")).lower()
    if any(tag in resolution_src for tag in _HIGH_RISK_RESOLUTION_SOURCES):
        score += 0.4

    # Contingent language in the question
    question = str(market.get("question", "")).lower()
    if any(kw in question for kw in _CONTINGENT_KEYWORDS):
        score += 0.3

    # Thin volume is a proxy for "market participants disagree / uncertain"
    try:
        vol = float(market.get("volume24hr", market.get("volume", 0)) or 0)
    except (ValueError, TypeError):
        vol = 0
    if vol < 5_000:
        score += 0.2
    elif vol < 20_000:
        score += 0.1

    return min(round(score, 2), 1.0)


# -- Entry point ---------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("PolyAlpha Protocol -- Arbitrage Scanner (Paper Trading Mode)")
    print("=" * 60)

    print("\n[1/2] Scanning Funding Rate Arbitrage...")
    funding_result = scan_funding_arbitrage(min_bps=30)
    funding_opps   = funding_result["data"]

    print("\n[2/2] Scanning PolyMarket Fast-Resolution...")
    poly_result = scan_polymarket_fast_resolution(min_price=0.95, max_hours_to_end=4)
    poly_opps   = poly_result["data"]

    print("\n" + "=" * 60)
    print(
        f"SCAN COMPLETE: {len(funding_opps)} funding arb [{funding_result['source'].upper()}] "
        f"+ {len(poly_opps)} PolyMarket [{poly_result['source'].upper()}] opportunities"
    )
    print("=" * 60)

    if funding_opps:
        print("\nTop Funding Arb:")
        for o in funding_opps:
            print(
                f"  {o['symbol']:6s} {o['long_venue']:12s} vs {o['short_venue']:12s} "
                f"net={o['net_spread_bps']}bps ann={o['annualized_pct']}%"
            )

    if poly_opps:
        print("\nTop PolyMarket Near-Settlement:")
        for o in poly_opps:
            print(
                f"  [{o['confidence_label']}] {o['question'][:55]}... "
                f"net={o['estimated_net_return_pct']*100:.1f}%"
            )
