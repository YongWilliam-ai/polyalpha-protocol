"""
news_client.py — Python port of 6551Team/daily-news API client.

Ported from daily-news/src/daily_news_mcp/api_client.py.
Implements MAX_RETRIES=2 exponential backoff, matching the original MCP server's
retry strategy exactly.

Public API:
    NewsAPIClient.get_crypto_sentiment(limit=10) -> str  # "BULLISH"|"BEARISH"|"NEUTRAL"
"""

import time
import logging
import requests
from typing import Optional

log = logging.getLogger("news_client")

NEWS_API_URL = "https://ai.6551.io/open/free_hot"
MAX_RETRIES  = 2
BASE_DELAY   = 1.0    # seconds; doubles on each retry


class NewsAPIClient:
    """
    Client for 6551Team/daily-news REST API.

    Mirrors api_client.py from the original daily-news MCP server:
        - MAX_RETRIES = 2 (initial attempt + 2 retries = 3 total attempts)
        - Exponential backoff: 1s, 2s
        - Handles both list and dict ({"data": [...]} / {"items": [...]}) response shapes
    """

    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout

    def _fetch_items(self, category: str = "crypto", limit: int = 10) -> Optional[list]:
        """
        Fetch hot news items with exponential backoff retry.
        Returns list of news item dicts, or None if all attempts fail.
        """
        delay = BASE_DELAY
        for attempt in range(1, MAX_RETRIES + 2):  # +2: initial attempt + MAX_RETRIES retries
            try:
                resp = requests.get(
                    NEWS_API_URL,
                    params={"category": category, "limit": limit},
                    timeout=self.timeout,
                )
                if resp.status_code == 200:
                    payload = resp.json()
                    if isinstance(payload, list):
                        return payload
                    if isinstance(payload, dict):
                        return payload.get(
                            "data",
                            payload.get("items", payload.get("list", [])),
                        )
                log.debug(f"News API HTTP {resp.status_code} (attempt {attempt})")
            except requests.exceptions.RequestException as exc:
                log.debug(f"News API error attempt {attempt}: {exc}")

            if attempt <= MAX_RETRIES:
                time.sleep(delay)
                delay *= 2

        return None

    def get_crypto_sentiment(self, limit: int = 10) -> str:
        """
        Fetch crypto news and classify macro sentiment.

        Each item carries a "signal" field: "bullish" | "bearish" | absent.
        Decision rule (6551Team spec):
            bullish > bearish + 2  ->  "BULLISH"
            bearish > bullish + 2  ->  "BEARISH"
            otherwise              ->  "NEUTRAL"

        The +2 buffer prevents a single headline from swinging the gate.
        Returns "NEUTRAL" on any API failure — never blocks the trading agent.
        """
        items = self._fetch_items(category="crypto", limit=limit)
        if not items:
            return "NEUTRAL"

        bullish = sum(1 for i in items if str(i.get("signal", "")).lower() == "bullish")
        bearish = sum(1 for i in items if str(i.get("signal", "")).lower() == "bearish")

        if bullish > bearish + 2:
            return "BULLISH"
        if bearish > bullish + 2:
            return "BEARISH"
        return "NEUTRAL"
