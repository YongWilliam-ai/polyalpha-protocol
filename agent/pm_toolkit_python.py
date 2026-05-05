"""
pm_toolkit_python.py — Python port of runesleo/polymarket-toolkit core data layer.

Ported from polymarket-toolkit/src/index.ts (TypeScript).
Uses requests with exponential backoff retry, mirroring the toolkit's
fetch-retry architecture (fetchClobMidpoint + fetchGammaMarkets).

Public API:
    fetch_clob_midpoint(market_id)  -> Optional[float]
    fetch_gamma_market(market_id)   -> Optional[float]
    get_yes_price(market_id)        -> Optional[float]  # primary with fallback
"""

import time
import logging
import requests
from typing import Optional

log = logging.getLogger("pm_toolkit")

CLOB_HOST       = "https://clob.polymarket.com"
GAMMA_API       = "https://gamma-api.polymarket.com"
MAX_RETRIES     = 3
BASE_DELAY_SEC  = 0.5    # seconds; doubles on each retry (exponential backoff)
REQUEST_TIMEOUT = 5.0    # seconds per attempt


def _get_with_retry(
    url: str,
    params: dict = None,
    retries: int = MAX_RETRIES,
    timeout: float = REQUEST_TIMEOUT,
) -> Optional[requests.Response]:
    """
    HTTP GET with exponential backoff retry.
    Returns Response on HTTP 200, None after all retries exhausted.
    """
    delay = BASE_DELAY_SEC
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, params=params, timeout=timeout)
            if resp.status_code == 200:
                return resp
            log.debug(f"HTTP {resp.status_code} from {url} (attempt {attempt}/{retries})")
        except requests.exceptions.RequestException as exc:
            log.debug(f"Request error {url} attempt {attempt}: {exc}")
        if attempt < retries:
            time.sleep(delay)
            delay *= 2
    return None


def fetch_clob_midpoint(market_id: str) -> Optional[float]:
    """
    Fetch live orderbook midpoint price from Polymarket CLOB REST API.
    Equivalent to fetchClobMidpoint() in polymarket-toolkit/src/index.ts.

    Endpoint: GET /midpoint?token_id={market_id}
    Returns YES token midpoint in [0, 1] or None on failure.
    """
    resp = _get_with_retry(f"{CLOB_HOST}/midpoint", params={"token_id": market_id})
    if resp is None:
        return None
    try:
        data = resp.json()
        mid = data.get("mid")
        return float(mid) if mid is not None else None
    except (ValueError, KeyError):
        return None


def fetch_gamma_market(market_id: str) -> Optional[float]:
    """
    Fetch YES price from Polymarket Gamma REST API.
    Equivalent to fetchGammaMarkets() in polymarket-toolkit/src/index.ts.

    Endpoint: GET /markets/{market_id}
    Returns outcomePrices[0] (YES probability in [0, 1]) or None on failure.
    """
    resp = _get_with_retry(f"{GAMMA_API}/markets/{market_id}")
    if resp is None:
        return None
    try:
        data = resp.json()
        prices = data.get("outcomePrices", [])
        return float(prices[0]) if prices else None
    except (ValueError, IndexError, KeyError):
        return None


def get_yes_price(market_id: str) -> Optional[float]:
    """
    Dual-source YES token price — mirrors polymarket-toolkit's primary/fallback strategy.

    Primary:  CLOB midpoint (live orderbook, lowest latency).
    Fallback: Gamma API (slightly stale but always available).

    Both sources have MAX_RETRIES=3 with exponential backoff before giving up.
    """
    price = fetch_clob_midpoint(market_id)
    if price is not None:
        return price
    return fetch_gamma_market(market_id)
