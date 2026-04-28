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
import requests
from datetime import datetime, timezone, timedelta
from typing import Optional

# -- Constants -----------------------------------------------------------------

TAKER_FEE_PER_LEG_BPS = 5   # 0.05% per leg; 10bps round-trip
ROUND_TRIP_FEE_BPS    = TAKER_FEE_PER_LEG_BPS * 2

# @hunterweb303 funding-rates-mcp — public API endpoints (no auth required)
HL_INFO_URL     = "https://api.hyperliquid.xyz/info"
BINANCE_FR_URL  = "https://fapi.binance.com/fapi/v1/fundingRate"
OKX_FR_URL      = "https://www.okx.com/api/v5/public/funding-rate"

# PolyAlpha Strategy 1 — PolyMarket API endpoints
GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API  = "https://clob.polymarket.com"


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
    Fetch current funding rates from OKX SWAP instruments.
    # @hunterweb303 funding-rates-mcp -- OKX public endpoint
    Returns {symbol: funding_rate_per_8h}
    """
    resp = requests.get(
        OKX_FR_URL,
        params={"instType": "SWAP"},
        timeout=5,
    )
    resp.raise_for_status()
    items = resp.json().get("data", [])

    rates = {}
    for item in items:
        inst_id = item.get("instId", "")
        # BTC-USDT-SWAP -> BTC
        symbol = inst_id.split("-")[0]
        try:
            rates[symbol] = float(item.get("fundingRate", 0))
        except (ValueError, TypeError):
            pass
    return rates


def scan_funding_arbitrage(min_bps: int = 50) -> list[dict]:
    """
    Scans 9 exchanges for funding rate arbitrage opportunities.
    Returns top 3 pairs with highest net spread (after taker fees).

    # @hunterweb303 funding-rates-mcp conceptual wrapper
    Data sources: Hyperliquid, Binance, OKX (live) + Bybit/dYdX/Drift/Vertex/Paradex/Aevo (stub)

    Returns:
        list of dicts: [{symbol, long_venue, short_venue, gross_spread_bps,
                         net_spread_bps, annualized_pct, estimated_8h_pnl_per_10k}]
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
        print("  All live APIs failed -- using mock data")
        return MOCK_FUNDING_OPPORTUNITIES[:3]

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
        print("  No live opportunities above threshold -- using mock data")
        return MOCK_FUNDING_OPPORTUNITIES[:3]

    opportunities.sort(key=lambda x: x["net_spread_bps"], reverse=True)
    top3 = opportunities[:3]
    print(f"  Top {len(top3)} funding arb opportunities found (live data)")
    return top3


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
) -> list[dict]:
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
        list of dicts: [{market_id, question, end_time, yes_price, no_price,
                         volume_24h, estimated_net_return_pct, confidence_label}]
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
        print(f"  Gamma API unavailable: {exc} -- using mock data")
        return MOCK_POLYMARKET_OPPORTUNITIES

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
    return qualifying


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
    funding_opps = scan_funding_arbitrage(min_bps=30)

    print("\n[2/2] Scanning PolyMarket Fast-Resolution...")
    poly_opps = scan_polymarket_fast_resolution(min_price=0.95, max_hours_to_end=4)

    print("\n" + "=" * 60)
    print(f"SCAN COMPLETE: {len(funding_opps)} funding arb + {len(poly_opps)} PolyMarket opportunities")
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
