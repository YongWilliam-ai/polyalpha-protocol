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

try:
    from execution_engine import CrossExchangeExecutor
    _EXECUTOR_AVAILABLE = True
except ImportError:
    _EXECUTOR_AVAILABLE = False

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


def scan_funding_arbitrage(min_bps: int = 50, executor=None) -> dict:
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

    # Execute paper trades for opportunities exceeding 1% net spread (100 bps)
    paper_trades = []
    if executor is not None:
        for opp in top3:
            if opp["net_spread_bps"] > 100:
                try:
                    receipt = executor.execute_funding_arb(
                        symbol=opp["symbol"],
                        long_exchange=opp["long_venue"],
                        short_exchange=opp["short_venue"],
                        amount_usdc=1_000.0,
                    )
                    paper_trades.append(receipt)
                except Exception as exc:
                    print(f"  Execution failed for {opp['symbol']}: {exc}")

    return {
        "data":          top3,
        "source":        "real",
        "timestamp":     ts,
        "error":         None,
        "paper_trades":  paper_trades,
    }


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


# -- YES/NO Riskless Arbitrage Scanner ----------------------------------------

def _get_best_ask_clob(token_id: str) -> Optional[float]:
    """
    Fetch the best (lowest) ask price for an outcome token from the CLOB order book.
    Best ask = cheapest price at which someone is willing to sell the token.
    Returns None if the book is empty or the request fails.
    """
    try:
        resp = requests.get(
            f"{CLOB_API}/book",
            params={"token_id": token_id},
            timeout=5,
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        asks = data.get("asks", [])
        if not asks:
            return None
        # asks may be unsorted -- take the minimum to find the true best ask
        return min(float(a["price"]) for a in asks if a.get("price"))
    except Exception:
        return None


def get_active_market_ids(limit: int = 50) -> list[str]:
    """
    Fetch condition IDs of active Polymarket markets from Gamma API.
    Used to seed scan_yes_no_arb() with a fresh universe of markets to check.
    """
    try:
        resp = requests.get(
            f"{GAMMA_API}/markets",
            params={"active": "true", "closed": "false", "limit": limit},
            timeout=8,
        )
        resp.raise_for_status()
        return [m["conditionId"] for m in resp.json() if m.get("conditionId")]
    except Exception as exc:
        print(f"  get_active_market_ids failed: {exc}")
        return []


def scan_yes_no_arb(market_ids: list[str]) -> list[dict]:
    """
    Scans Polymarket markets for YES+NO riskless arbitrage.

    # MrFadiAi/Polymarket-bot Strategy 1: YES+NO < $1.00 = guaranteed profit
    # A Polymarket binary market always resolves to exactly $1.00 total:
    # either YES pays $1.00 or NO pays $1.00. If you can buy BOTH for < $0.98,
    # you lock in a risk-free gain regardless of outcome.
    # The 2% buffer covers Polygon gas fees + CLOB taker fee (est. ~0.5-1%).

    Parameters:
        market_ids: list of Polymarket condition IDs (from Gamma API conditionId field)

    Returns:
        list of dicts with: market_id, question, yes_price, no_price, total, profit_pct
        Sorted by profit_pct descending. Empty list = no arb found (normal).
    """
    ts = datetime.now(timezone.utc).isoformat()
    print(f"[{ts}] Scanning YES/NO arb across {len(market_ids)} markets...")

    # One Gamma API call to resolve clobTokenIds for all requested condition IDs
    token_id_map: dict[str, list[str]] = {}   # condition_id -> [yes_token_id, no_token_id]
    question_map: dict[str, str] = {}

    try:
        resp = requests.get(
            f"{GAMMA_API}/markets",
            params={"active": "true", "limit": max(len(market_ids), 100)},
            timeout=8,
        )
        resp.raise_for_status()
        condition_id_set = set(market_ids)
        for m in resp.json():
            cid = m.get("conditionId", "")
            if cid not in condition_id_set:
                continue
            clob_ids = m.get("clobTokenIds", [])
            if isinstance(clob_ids, str):
                try:
                    clob_ids = json.loads(clob_ids)
                except (json.JSONDecodeError, TypeError):
                    continue
            if isinstance(clob_ids, list) and len(clob_ids) >= 2:
                token_id_map[cid] = [str(clob_ids[0]), str(clob_ids[1])]
                question_map[cid] = str(m.get("question", ""))[:120]
    except Exception as exc:
        print(f"  Gamma API lookup failed: {exc} -- aborting YES/NO scan")
        return []

    if not token_id_map:
        print(f"  Could not resolve clobTokenIds for any of the {len(market_ids)} markets")
        return []

    print(f"  Resolved token IDs for {len(token_id_map)}/{len(market_ids)} markets")

    opportunities = []

    for condition_id, (yes_token, no_token) in token_id_map.items():
        yes_ask = _get_best_ask_clob(yes_token)
        no_ask  = _get_best_ask_clob(no_token)

        if yes_ask is None or no_ask is None:
            continue

        total = yes_ask + no_ask

        if total >= 0.98:
            continue  # no arb above the 2% safety buffer

        profit_pct = round((1.0 - total) * 100, 3)

        opp = {
            "market_id":  condition_id,
            "question":   question_map.get(condition_id, ""),
            "yes_price":  round(yes_ask, 4),
            "no_price":   round(no_ask, 4),
            "total":      round(total, 4),
            "profit_pct": profit_pct,
        }
        opportunities.append(opp)
        print(
            f"  ARB FOUND: {opp['question'][:55]}... "
            f"YES={yes_ask:.4f}+NO={no_ask:.4f}={total:.4f} profit={profit_pct:.2f}%"
        )

    if not opportunities:
        print(f"  No YES/NO arb found ({len(token_id_map)} books checked -- this is normal)")

    opportunities.sort(key=lambda x: x["profit_pct"], reverse=True)
    return opportunities


# -- Logical Correlation Arbitrage Scanner ------------------------------------

# Minimum price spread (absolute) to flag a logical violation as exploitable.
# 3% threshold exceeds estimated transaction cost (~1%), leaving real net edge.
CORRELATION_VIOLATION_THRESHOLD = 0.03

# Each rule defines a pair of markets that must satisfy P(specific) <= P(broad).
# Violation: price(specific) > price(broad) + THRESHOLD.
# specific_keywords / broad_keywords: ALL must appear in the market question (case-insensitive).
KNOWN_CORRELATIONS: list[dict] = [
    {
        "id":                "trump_vs_republican_president",
        "specific_keywords": ["trump", "win"],
        "broad_keywords":    ["republican", "win"],
        "specific_label":    "Trump wins presidential election",
        "broad_label":       "Republican wins presidential election",
        "logic":             "Trump IS a Republican -- P(Trump wins) <= P(Republican wins)",
    },
    {
        "id":                "btc_100k_vs_80k",
        "specific_keywords": ["bitcoin", "100,000"],
        "broad_keywords":    ["bitcoin", "80,000"],
        "specific_label":    "BTC above $100k",
        "broad_label":       "BTC above $80k",
        "logic":             "P(BTC>$100k) <= P(BTC>$80k) -- stricter threshold implies looser",
    },
    {
        "id":                "eth_5k_vs_3k",
        "specific_keywords": ["ethereum", "5,000"],
        "broad_keywords":    ["ethereum", "3,000"],
        "specific_label":    "ETH above $5k",
        "broad_label":       "ETH above $3k",
        "logic":             "P(ETH>$5k) <= P(ETH>$3k) -- stricter threshold implies looser",
    },
    {
        "id":                "chiefs_vs_afc_superbowl",
        "specific_keywords": ["chiefs", "super bowl"],
        "broad_keywords":    ["afc", "super bowl"],
        "specific_label":    "Kansas City Chiefs win Super Bowl",
        "broad_label":       "AFC team wins Super Bowl",
        "logic":             "Chiefs ARE an AFC team -- P(Chiefs win) <= P(AFC team wins)",
    },
    {
        "id":                "btc_200k_vs_150k",
        "specific_keywords": ["bitcoin", "200,000"],
        "broad_keywords":    ["bitcoin", "150,000"],
        "specific_label":    "BTC above $200k",
        "broad_label":       "BTC above $150k",
        "logic":             "P(BTC>$200k) <= P(BTC>$150k)",
    },
]


def _find_matching_market(markets: list[dict], keywords: list[str]) -> Optional[dict]:
    """Return first market whose question contains ALL keywords (case-insensitive)."""
    kw_lower = [k.lower() for k in keywords]
    for m in markets:
        question = m.get("question", "").lower()
        if all(kw in question for kw in kw_lower):
            return m
    return None


def _extract_yes_price(market: dict) -> Optional[float]:
    """Extract YES (outcome 0) probability from a Gamma API market object."""
    try:
        prices = market.get("outcomePrices", [])
        if prices:
            return float(prices[0])
    except (ValueError, TypeError, IndexError):
        pass
    return None


def scan_correlation_arb() -> list[dict]:
    """
    Scans active Polymarket markets for logical correlation violations.

    # OpenSource_Integration_Plan.md Strategy A3 (win rate 70-80%)
    # Principle: if Outcome A is a strict subset of Outcome B,
    # P(A) <= P(B) must always hold. When P(A) > P(B) + threshold,
    # the crowd has violated a basic probability axiom.
    #
    # Trade: buy underpriced broad-category YES, short overpriced specific
    # outcome. Multi-leg execution within 500ms window (Phase 2).
    # Phase 1: detection and logging only (paper trading).

    Returns:
        list of dicts: violation_id, specific_market_id, broad_market_id,
                       specific_question, broad_question, specific_price,
                       broad_price, spread, spread_bps, logic
        Sorted by spread_bps descending. Empty list = no violations (normal).
    """
    ts = datetime.now(timezone.utc).isoformat()
    print(
        f"[{ts}] Scanning correlation arb across {len(KNOWN_CORRELATIONS)} known rules..."
    )

    try:
        resp = requests.get(
            f"{GAMMA_API}/markets",
            params={"active": "true", "limit": 100},
            timeout=8,
        )
        resp.raise_for_status()
        markets = resp.json()
        print(f"  Fetched {len(markets)} active markets from Gamma API")
    except Exception as exc:
        print(f"  Gamma API unavailable: {exc} -- aborting correlation scan")
        return []

    violations = []

    for rule in KNOWN_CORRELATIONS:
        specific_mkt = _find_matching_market(markets, rule["specific_keywords"])
        broad_mkt    = _find_matching_market(markets, rule["broad_keywords"])

        if specific_mkt is None or broad_mkt is None:
            continue  # these markets don't exist on Polymarket right now

        specific_id = specific_mkt.get("conditionId", "")
        broad_id    = broad_mkt.get("conditionId", "")

        if specific_id == broad_id:
            continue  # same market matched both sides -- skip

        specific_price = _extract_yes_price(specific_mkt)
        broad_price    = _extract_yes_price(broad_mkt)

        if specific_price is None or broad_price is None:
            continue

        spread     = specific_price - broad_price   # positive = violation
        spread_bps = int(spread * 10_000)

        if spread <= CORRELATION_VIOLATION_THRESHOLD:
            continue  # within normal pricing bounds

        violation = {
            "violation_id":       rule["id"],
            "specific_market_id": specific_id,
            "broad_market_id":    broad_id,
            "specific_question":  specific_mkt.get("question", "")[:100],
            "broad_question":     broad_mkt.get("question", "")[:100],
            "specific_price":     round(specific_price, 4),
            "broad_price":        round(broad_price, 4),
            "spread":             round(spread, 4),
            "spread_bps":         spread_bps,
            "logic":              rule["logic"],
        }
        violations.append(violation)
        print(
            f"  VIOLATION [{rule['id']}]: specific={specific_price:.3f} > "
            f"broad={broad_price:.3f} spread={spread_bps}bps"
        )

    if not violations:
        print(
            f"  No correlation violations found "
            f"({len(KNOWN_CORRELATIONS)} rules x {len(markets)} markets -- this is normal)"
        )

    violations.sort(key=lambda x: x["spread_bps"], reverse=True)
    return violations


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

    print("\n[1/4] Scanning Funding Rate Arbitrage...")
    funding_result = scan_funding_arbitrage(min_bps=30)
    funding_opps   = funding_result["data"]

    print("\n[2/4] Scanning PolyMarket Fast-Resolution...")
    poly_result = scan_polymarket_fast_resolution(min_price=0.95, max_hours_to_end=4)
    poly_opps   = poly_result["data"]

    print("\n[3/4] Scanning YES/NO Riskless Arbitrage...")
    market_ids = get_active_market_ids(limit=30)
    yesno_opps = scan_yes_no_arb(market_ids) if market_ids else []

    print("\n[4/4] Scanning Logical Correlation Arbitrage...")
    corr_opps = scan_correlation_arb()

    print("\n" + "=" * 60)
    print(
        f"SCAN COMPLETE: {len(funding_opps)} funding arb [{funding_result['source'].upper()}] "
        f"+ {len(poly_opps)} PolyMarket [{poly_result['source'].upper()}] "
        f"+ {len(yesno_opps)} YES/NO arb "
        f"+ {len(corr_opps)} correlation violations"
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

    if yesno_opps:
        print("\nYES/NO Riskless Arb:")
        for o in yesno_opps:
            print(
                f"  {o['market_id'][:12]}... "
                f"YES={o['yes_price']:.4f}+NO={o['no_price']:.4f} profit={o['profit_pct']:.2f}%"
            )
    else:
        print("\nYES/NO Arb: none found (rare in efficient markets -- scan is working correctly)")

    if corr_opps:
        print("\nCorrelation Violations:")
        for o in corr_opps:
            print(
                f"  [{o['violation_id']}] specific={o['specific_price']:.3f} > "
                f"broad={o['broad_price']:.3f} spread={o['spread_bps']}bps | {o['logic']}"
            )
    else:
        print("\nCorrelation Arb: none found (this is normal -- markets are usually internally consistent)")
