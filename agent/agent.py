"""
agent.py -- PolyAlpha AI Signal Agent (Paper Trading Mode)

Pipeline:
  scan()         -> fetch active BTC 15m markets from Polymarket Gamma API
  generate()     -> btc_signal.py deterministic momentum rule -> BtcSignal
  safety_check() -> 6-step BitPilot-inspired safety chain before any execution
  log_on_chain() -> call vault.logPosition() via web3.py -> PositionLogged event
  monitor()      -> loop every 60s, log all valid signals, skip if halted

Paper trading mode (v1):
  The agent LOGS signals on-chain but does NOT execute trades via CLOB.
  This proves the signal pipeline works and creates a verifiable audit trail.
  Actual execution is deferred to v2 (post-submission).

======================================================================
POLYMARKET V2 MIGRATION NOTE (April 22, 2026)
======================================================================
Polymarket V1 is now deprecated. V2 changes:
  - Collateral:  USDC.e -> pUSD (new stablecoin)
  - SDK:         py-clob-client -> py-clob-client-v2
  - Order fields: nonce + feeRateBps removed; timestamp + builder added
  - Contracts:   New exchange contract addresses on Polygon mainnet

Impact on this agent:
  - Vault contract: NOT affected (uses MockUSDC for simulation)
  - Gamma API reads: STILL WORK (price feeds are V2-compatible)
  - CLOB execution: MUST upgrade to py-clob-client-v2 before live trading
  - get_polymarket_v2_price() stub below is ready for V2 SDK integration

Migration guide: https://docs.polymarket.com/v2-migration
======================================================================

To run:
  cd agent && python agent.py

Requirements:
  .env with VAULT_CONTRACT_ADDRESS, PRIVATE_KEY, AMOY_RPC_URL
  pip install -r requirements.txt
"""

import os
import sys
import time
import json
import logging
from datetime import datetime, timezone
from typing import Optional

import requests
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account

from btc_signal import (
    generate_signal,
    BtcSignal,
    get_btc_price_now,
    get_btc_price_n_minutes_ago,
    dual_source_oracle_check,
    EDGE_MIN_BPS,
    EDGE_MAX_BPS,
    MAX_POSITION_BPS,
)

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

# -- Logging setup ------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("agent_log.jsonl"),
    ],
)
log = logging.getLogger("polyalpha")

# -- Config -------------------------------------------------------------------
GAMMA_API            = "https://gamma-api.polymarket.com"
CLOB_V2_API          = "https://clob.polymarket.com"     # V2 price API base
SCAN_INTERVAL_SEC    = 60
MAX_MARKETS_TO_SCAN  = 30
MIN_MARKET_LIQUIDITY = 50_000   # $50K minimum

# Daily loss limit for Step 5 of the safety chain (15% of TVL equiv)
DAILY_LOSS_LIMIT_BPS = 1_500   # 15%

VAULT_ABI = [
    {
        "name": "logPosition",
        "type": "function",
        "inputs": [
            {"name": "marketQuestion",   "type": "string"},
            {"name": "aiProbabilityBps", "type": "uint256"},
            {"name": "marketPriceBps",   "type": "uint256"},
            {"name": "side",             "type": "string"},
            {"name": "kellyFractionBps", "type": "uint256"},
            {"name": "oracleInputHash",  "type": "bytes32"},
        ],
        "outputs": [],
        "stateMutability": "nonpayable",
    },
    {
        "name": "halted",
        "type": "function",
        "inputs": [],
        "outputs": [{"type": "bool"}],
        "stateMutability": "view",
    },
    {
        "name": "totalAssets",
        "type": "function",
        "inputs": [],
        "outputs": [{"type": "uint256"}],
        "stateMutability": "view",
    },
]


# -- Polymarket V2: price fetch stub ------------------------------------------

def get_polymarket_v2_price(market_id: str) -> Optional[float]:
    """
    [V2 STUB] Fetch YES token best-bid price from Polymarket V2 CLOB API.

    Polymarket V2 order structure (post April 22, 2026):
      - Removed: nonce, feeRateBps
      - Added:   timestamp (Unix ms), builder (address)
      - Collateral: pUSD (not USDC.e)

    TODO (v2 live trading): Replace with py-clob-client-v2 SDK call:
        from py_clob_client.client import ClobClient
        client = ClobClient(host="https://clob.polymarket.com", chain_id=137)
        book = client.get_order_book(token_id=market_id)
        return float(book.bids[0].price) if book.bids else None

    Current implementation: direct REST call to V2 CLOB (no SDK needed for reads).
    Falls back to None on any error; caller uses Gamma API as fallback.

    Ref: https://docs.polymarket.com/v2-migration
    """
    try:
        resp = requests.get(
            f"{CLOB_V2_API}/book",
            params={"token_id": market_id},
            timeout=5,
        )
        if resp.status_code == 200:
            book = resp.json()
            bids = book.get("bids", [])
            if bids:
                return float(bids[0]["price"])
    except Exception:
        pass
    return None


# -- 6-step safety chain ------------------------------------------------------

def safety_check_chain(
    signal: BtcSignal,
    vault=None,
    daily_loss_tracker: Optional[dict] = None,
) -> tuple[bool, str]:
    """
    6-step BitPilot-inspired safety chain.
    Every step must pass before a signal is submitted on-chain.
    Returns (True, "OK") to proceed, or (False, reason_string) to abort.

    Step 1: Signal confidence     -- edge must meet minimum threshold
    Step 2: Position size         -- Kelly size within hard cap
    Step 3: Circuit breaker       -- vault must not be halted
    Step 4: Oracle cross-check    -- dual-source divergence within limit
    Step 5: Daily loss limit      -- cumulative daily loss within bound
    Step 6: Decision log          -- record timestamp and params before acting

    Inspired by: duolaAmengweb3/bgtask (BitPilot) 7x24 daemon pattern
    """

    # Step 1: Signal confidence >= EDGE_MIN_BPS
    if signal.edge_bps < EDGE_MIN_BPS:
        return False, (
            f"[Safety Step 1] Edge {signal.edge_bps}bps < min {EDGE_MIN_BPS}bps"
        )

    # Step 2: Position size within MAX_POSITION_BPS cap
    if signal.kelly_bps > MAX_POSITION_BPS:
        return False, (
            f"[Safety Step 2] Kelly {signal.kelly_bps}bps > cap {MAX_POSITION_BPS}bps"
        )

    # Step 3: Vault circuit breaker not triggered
    if vault is not None:
        try:
            if vault.functions.halted().call():
                return False, "[Safety Step 3] Vault circuit breaker is ACTIVE -- halted"
        except Exception as exc:
            return False, f"[Safety Step 3] Cannot read vault state: {exc}"

    # Step 4: Oracle cross-validation (dual-source divergence check)
    if not dual_source_oracle_check(signal.ai_probability, signal.market_price):
        return False, (
            f"[Safety Step 4] Divergence {abs(signal.ai_probability - signal.market_price)*100:.1f}% "
            f"exceeds {EDGE_MAX_BPS / 100:.0f}% limit -- possible data anomaly"
        )

    # Step 5: Daily loss limit not exceeded
    if daily_loss_tracker is not None:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        daily_loss_bps = daily_loss_tracker.get(today, 0)  # negative = loss in bps
        if daily_loss_bps <= -DAILY_LOSS_LIMIT_BPS:
            return False, (
                f"[Safety Step 5] Daily loss {daily_loss_bps}bps <= "
                f"-{DAILY_LOSS_LIMIT_BPS}bps limit -- no new positions today"
            )

    # Step 6: Log the decision with full context before acting
    decision_record = {
        "ts":           datetime.now(timezone.utc).isoformat(),
        "safety_chain": "PASSED",
        "market":       signal.market_question[:60],
        "side":         signal.side,
        "edge_bps":     signal.edge_bps,
        "kelly_bps":    signal.kelly_bps,
        "ai_prob":      round(signal.ai_probability, 4),
        "market_price": round(signal.market_price, 4),
        "oracle_hash":  signal.oracle_hash[:18] + "...",
    }
    log.info(f"  [Safety Chain PASS] {json.dumps(decision_record)}")

    return True, "OK"


# -- Web3 setup ---------------------------------------------------------------

def build_web3_connection() -> tuple[Web3, object, str]:
    """Connect to Polygon Amoy and load the vault contract."""
    rpc = os.getenv("AMOY_RPC_URL", "https://rpc-amoy.polygon.technology/")
    w3  = Web3(Web3.HTTPProvider(rpc))

    if not w3.is_connected():
        raise ConnectionError(f"Cannot connect to RPC: {rpc}")

    vault_addr = os.getenv("VAULT_CONTRACT_ADDRESS")
    if not vault_addr:
        raise ValueError("VAULT_CONTRACT_ADDRESS not set in .env -- run deploy.js first")

    vault = w3.eth.contract(
        address=Web3.to_checksum_address(vault_addr),
        abi=VAULT_ABI,
    )

    agent_wallet = os.getenv("PRIVATE_KEY")
    if not agent_wallet:
        raise ValueError("PRIVATE_KEY not set in .env")

    account = Account.from_key(agent_wallet)
    log.info(f"Agent wallet: {account.address}")
    log.info(f"Vault:        {vault_addr}")
    log.info(f"Network:      Polygon Amoy (chain {w3.eth.chain_id})")

    return w3, vault, account.address


# -- Market scanning ----------------------------------------------------------

def scan_btc_markets() -> list[dict]:
    """Fetch active BTC Up/Down 15m markets from Polymarket Gamma API.
    Gamma API still works in V2 for price reads -- no SDK migration needed here.
    """
    url = f"{GAMMA_API}/markets"
    params = {
        "active": "true",
        "closed": "false",
        "limit":  MAX_MARKETS_TO_SCAN,
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    markets = resp.json()

    btc_markets = [
        m for m in markets
        if ("bitcoin" in m.get("question", "").lower()
            or "btc" in m.get("question", "").lower())
        and float(m.get("liquidity", 0)) >= MIN_MARKET_LIQUIDITY
    ]
    return btc_markets


def get_yes_price(market: dict) -> float:
    """
    Extract YES token price (0-1) from market data.
    Tries V2 CLOB price first; falls back to Gamma API outcomePrices.
    """
    # Try V2 CLOB price (more accurate for live trading)
    token_id = market.get("clobTokenIds", [None])[0]
    if token_id:
        v2_price = get_polymarket_v2_price(token_id)
        if v2_price is not None:
            return v2_price

    # Fallback: Gamma API outcome prices
    outcomes = market.get("outcomePrices", [])
    if outcomes:
        try:
            return float(outcomes[0])
        except (ValueError, IndexError):
            pass

    return float(market.get("bestBid", 0.5))


# -- News sentiment pre-filter ------------------------------------------------

def get_news_sentiment() -> str:
    """
    Fetch crypto news sentiment from 6551 AI hot news API.

    # Inspired by 6551Team/daily-news MCP Server
    Endpoint: https://ai.6551.io/open/free_hot?category=crypto (no API key)

    Returns "bullish", "bearish", or "neutral".
    Used as a trade pre-filter: skip UP signals when sentiment is bearish
    to avoid fighting macro news flow with a pure momentum signal.

    Falls back to "neutral" on any network error so the agent keeps running.
    """
    # Inspired by 6551Team/daily-news MCP Server
    BULLISH_KEYWORDS = {
        "surge", "rally", "gain", "rise", "bull", "pump",
        "breakout", "high", "record", "green", "rebound",
    }
    BEARISH_KEYWORDS = {
        "crash", "drop", "fall", "bear", "dump", "plunge",
        "low", "decline", "red", "fear", "sell-off", "collapse",
    }

    try:
        resp = requests.get(
            "https://ai.6551.io/open/free_hot",
            params={"category": "crypto"},
            timeout=5,
        )
        if resp.status_code != 200:
            return "neutral"

        payload = resp.json()
        items = (
            payload if isinstance(payload, list)
            else payload.get("data", payload.get("items", []))
        )

        bullish = 0
        bearish = 0
        for item in items[:10]:  # only top 10 headlines
            if isinstance(item, dict):
                text = " ".join([
                    item.get("title", ""),
                    item.get("content", ""),
                    item.get("summary", ""),
                ]).lower()
            else:
                text = str(item).lower()

            bullish += sum(1 for kw in BULLISH_KEYWORDS if kw in text)
            bearish += sum(1 for kw in BEARISH_KEYWORDS if kw in text)

        if bearish > bullish + 2:
            return "bearish"
        if bullish > bearish + 2:
            return "bullish"
        return "neutral"

    except Exception:
        return "neutral"  # safe default -- never block the agent on a news API failure


# -- On-chain logging ---------------------------------------------------------

def log_position_on_chain(
    w3: Web3,
    vault,
    private_key: str,
    signal: BtcSignal,
) -> str:
    """
    Call vault.logPosition() to record the signal immutably on-chain.
    Returns the transaction hash.
    """
    account = Account.from_key(private_key)
    oracle_bytes = bytes.fromhex(signal.oracle_hash.removeprefix("0x"))

    nonce     = w3.eth.get_transaction_count(account.address)
    gas_price = w3.eth.gas_price

    tx = vault.functions.logPosition(
        signal.market_question[:200],
        signal.ai_prob_bps,
        signal.market_price_bps,
        signal.side,
        signal.kelly_bps,
        oracle_bytes,
    ).build_transaction({
        "from":     account.address,
        "nonce":    nonce,
        "gasPrice": gas_price,
        "gas":      200_000,
        "chainId":  80002,  # Polygon Amoy
    })

    signed   = account.sign_transaction(tx)
    tx_hash  = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt  = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

    return receipt.transactionHash.hex()


# -- Main agent loop ----------------------------------------------------------

def run_agent(dry_run: bool = False):
    """
    Main agent loop.

    dry_run=True: generate signals and print them, do NOT submit on-chain.
                  Use this for testing before vault is deployed.
    """
    log.info("=" * 60)
    log.info("PolyAlpha Agent Starting (V2.0)")
    log.info(f"Mode: {'DRY RUN (no on-chain logging)' if dry_run else 'LIVE (logging on-chain)'}")
    log.info("=" * 60)

    if not dry_run:
        w3, vault, agent_addr = build_web3_connection()
        private_key = os.getenv("PRIVATE_KEY")
    else:
        w3, vault, agent_addr, private_key = None, None, "0x0", None

    # Daily loss tracker: {"YYYY-MM-DD": cumulative_loss_bps}
    daily_loss_tracker: dict = {}
    # Rolling trade history for empirical Kelly sizing ({"won": bool} records)
    trade_history: list = []

    signals_logged = 0
    scan_count     = 0

    while True:
        scan_count += 1
        log.info(f"\n-- Scan #{scan_count} @ {datetime.now(timezone.utc).isoformat()} --")

        # Check if vault is halted (also covered by safety chain Step 3)
        if not dry_run and vault:
            try:
                if vault.functions.halted().call():
                    log.warning("Vault circuit breaker is ACTIVE. Skipping scan.")
                    time.sleep(SCAN_INTERVAL_SEC)
                    continue
            except Exception as exc:
                log.warning(f"Could not read vault state: {exc}")

        # News sentiment pre-filter (6551Team/daily-news -- one call per scan)
        sentiment = get_news_sentiment()
        log.info(f"News sentiment: {sentiment}")

        # Fetch BTC prices once per scan cycle
        try:
            btc_now  = get_btc_price_now()
            btc_open = get_btc_price_n_minutes_ago(7)
            delta_pct = (btc_now - btc_open) / btc_open * 100
            log.info(
                f"BTC: open=${btc_open:,.2f}  now=${btc_now:,.2f}  "
                f"delta={delta_pct:+.3f}%"
            )
        except Exception as exc:
            log.error(f"BTC price fetch failed: {exc}")
            time.sleep(SCAN_INTERVAL_SEC)
            continue

        # Scan markets
        try:
            markets = scan_btc_markets()
            log.info(
                f"Markets found: {len(markets)} BTC markets above "
                f"${MIN_MARKET_LIQUIDITY:,} liquidity"
            )
        except Exception as exc:
            log.error(f"Market scan failed: {exc}")
            time.sleep(SCAN_INTERVAL_SEC)
            continue

        # Generate and process signals
        for market in markets:
            question     = market.get("question", "")
            condition_id = market.get("conditionId", "")
            yes_price    = get_yes_price(market)
            liquidity    = float(market.get("liquidity", 0))

            signal = generate_signal(
                market_question=question,
                condition_id=condition_id,
                market_price=yes_price,
                liquidity_usd=liquidity,
                btc_open=btc_open,
                btc_now=btc_now,
                trade_history=trade_history,
            )

            if signal is None:
                continue

            # Sentiment pre-filter: skip UP signals when news is bearish
            if signal.side == "UP" and sentiment == "bearish":
                log.info(
                    f"  [Sentiment Filter] Skipping UP signal -- news is bearish"
                )
                continue

            log.info(str(signal))

            # --- 6-step safety chain BEFORE any execution --------------------
            safe, reason = safety_check_chain(
                signal=signal,
                vault=vault if not dry_run else None,
                daily_loss_tracker=daily_loss_tracker,
            )
            if not safe:
                log.warning(f"  [Safety Chain BLOCKED] {reason}")
                continue
            # -----------------------------------------------------------------

            signal_record = {
                "ts":               signal.timestamp,
                "market":           question[:80],
                "condition_id":     condition_id,
                "side":             signal.side,
                "btc_momentum_pct": round(signal.btc_momentum * 100, 4),
                "market_price":     round(signal.market_price, 4),
                "ai_probability":   round(signal.ai_probability, 4),
                "edge_bps":         signal.edge_bps,
                "kelly_bps":        signal.kelly_bps,
                "oracle_hash":      signal.oracle_hash,
                "dry_run":          dry_run,
            }

            if dry_run:
                log.info(f"  [DRY RUN] Signal: {json.dumps(signal_record)}")
                signals_logged += 1
                # Paper trade -- assume neutral outcome for history tracking
                trade_history.append({"won": None})
            else:
                try:
                    tx_hash = log_position_on_chain(w3, vault, private_key, signal)
                    signal_record["tx_hash"] = tx_hash
                    log.info(
                        f"  On-chain: https://amoy.polygonscan.com/tx/{tx_hash}"
                    )
                    signals_logged += 1
                except Exception as exc:
                    log.error(f"  logPosition() failed: {exc}")

        log.info(
            f"Signals this session: {signals_logged} | "
            f"Next scan in {SCAN_INTERVAL_SEC}s"
        )
        time.sleep(SCAN_INTERVAL_SEC)


# -- Entry point --------------------------------------------------------------

if __name__ == "__main__":
    vault_deployed = bool(os.getenv("VAULT_CONTRACT_ADDRESS"))
    dry = not vault_deployed

    if dry:
        print("VAULT_CONTRACT_ADDRESS not set -- running in DRY RUN mode (no on-chain logging)")
        print("Deploy the vault first: npm run deploy:amoy\n")

    run_agent(dry_run=dry)
