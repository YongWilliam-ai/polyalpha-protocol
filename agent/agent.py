"""
agent.py — PolyAlpha AI Signal Agent (Paper Trading Mode)

Pipeline:
  scan()         → fetch active BTC 15m markets from Polymarket Gamma API
  generate()     → btc_signal.py deterministic momentum rule → BtcSignal
  log_on_chain() → call vault.logPosition() via web3.py → PositionLogged event
  monitor()      → loop every 60s, log all valid signals, skip if halted

Paper trading mode (v1):
  The agent LOGS signals on-chain but does NOT execute trades via CLOB.
  This proves the signal pipeline works and creates a verifiable audit trail.
  Actual execution is deferred to v2 (post-submission).

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

import requests
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account

from btc_signal import generate_signal, BtcSignal, get_btc_price_now, get_btc_price_n_minutes_ago

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("agent_log.jsonl"),
    ],
)
log = logging.getLogger("polyalpha")

# ── Config ────────────────────────────────────────────────────────────────────
GAMMA_API            = "https://gamma-api.polymarket.com"
SCAN_INTERVAL_SEC    = 60       # Scan every 60 seconds
MAX_MARKETS_TO_SCAN  = 30       # Limit per scan cycle
MIN_MARKET_LIQUIDITY = 50_000   # $50K minimum

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


# ── Web3 setup ────────────────────────────────────────────────────────────────

def build_web3_connection() -> tuple[Web3, object, str]:
    """Connect to Polygon Amoy and load the vault contract."""
    rpc = os.getenv("AMOY_RPC_URL", "https://rpc-amoy.polygon.technology/")
    w3  = Web3(Web3.HTTPProvider(rpc))

    if not w3.is_connected():
        raise ConnectionError(f"Cannot connect to RPC: {rpc}")

    vault_addr = os.getenv("VAULT_CONTRACT_ADDRESS")
    if not vault_addr:
        raise ValueError("VAULT_CONTRACT_ADDRESS not set in .env — run deploy.js first")

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


# ── Market scanning ───────────────────────────────────────────────────────────

def scan_btc_markets() -> list[dict]:
    """Fetch active BTC Up/Down 15m markets from Polymarket Gamma API."""
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
        if ("bitcoin" in m.get("question", "").lower() or "btc" in m.get("question", "").lower())
        and float(m.get("liquidity", 0)) >= MIN_MARKET_LIQUIDITY
    ]
    return btc_markets


def get_yes_price(market: dict) -> float:
    """Extract YES token price (0–1) from market data."""
    # Try outcome prices first
    outcomes = market.get("outcomePrices", [])
    if outcomes:
        try:
            return float(outcomes[0])  # index 0 = YES
        except (ValueError, IndexError):
            pass
    # Fallback: use bestBid
    return float(market.get("bestBid", 0.5))


# ── On-chain logging ──────────────────────────────────────────────────────────

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

    # Convert oracle hash string to bytes32
    oracle_bytes = bytes.fromhex(signal.oracle_hash.removeprefix("0x"))

    # Build transaction
    nonce    = w3.eth.get_transaction_count(account.address)
    gas_price = w3.eth.gas_price

    tx = vault.functions.logPosition(
        signal.market_question[:200],   # truncate if too long
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

    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

    return receipt.transactionHash.hex()


# ── Main agent loop ───────────────────────────────────────────────────────────

def run_agent(dry_run: bool = False):
    """
    Main agent loop.

    dry_run=True: generate signals and print them but do NOT submit on-chain.
                  Use this for testing before vault is deployed.
    """
    log.info("=" * 60)
    log.info("PolyAlpha Agent Starting")
    log.info(f"Mode: {'DRY RUN (no on-chain logging)' if dry_run else 'LIVE (logging on-chain)'}")
    log.info("=" * 60)

    if not dry_run:
        w3, vault, agent_addr = build_web3_connection()
        private_key = os.getenv("PRIVATE_KEY")
    else:
        w3, vault, agent_addr, private_key = None, None, "0x0", None

    signals_logged = 0
    scan_count     = 0

    while True:
        scan_count += 1
        log.info(f"\n── Scan #{scan_count} @ {datetime.now(timezone.utc).isoformat()} ──")

        # Check if vault is halted
        if not dry_run and vault:
            try:
                is_halted = vault.functions.halted().call()
                if is_halted:
                    log.warning("🛑 Vault circuit breaker is ACTIVE. Skipping scan.")
                    time.sleep(SCAN_INTERVAL_SEC)
                    continue
            except Exception as e:
                log.warning(f"Could not read vault state: {e}")

        # Fetch BTC prices once per scan (shared across all markets)
        try:
            btc_now  = get_btc_price_now()
            btc_open = get_btc_price_n_minutes_ago(7)
            log.info(f"BTC: open=${btc_open:,.2f}  now=${btc_now:,.2f}  Δ={(btc_now-btc_open)/btc_open*100:+.3f}%")
        except Exception as e:
            log.error(f"BTC price fetch failed: {e}")
            time.sleep(SCAN_INTERVAL_SEC)
            continue

        # Scan markets
        try:
            markets = scan_btc_markets()
            log.info(f"Markets found: {len(markets)} BTC markets above ${MIN_MARKET_LIQUIDITY:,} liquidity")
        except Exception as e:
            log.error(f"Market scan failed: {e}")
            time.sleep(SCAN_INTERVAL_SEC)
            continue

        # Generate and process signals
        for market in markets:
            question     = market.get("question", "")
            condition_id = market.get("conditionId", "")
            yes_price    = get_yes_price(market)
            liquidity    = float(market.get("liquidity", 0))

            signal = generate_signal(
                market_question = question,
                condition_id    = condition_id,
                market_price    = yes_price,
                liquidity_usd   = liquidity,
                btc_open        = btc_open,
                btc_now         = btc_now,
            )

            if signal is None:
                continue

            log.info(str(signal))

            # Structured signal for JSONL log (for backtest/analysis)
            signal_record = {
                "ts":             signal.timestamp,
                "market":         question[:80],
                "condition_id":   condition_id,
                "side":           signal.side,
                "btc_momentum_pct": round(signal.btc_momentum * 100, 4),
                "market_price":   round(signal.market_price, 4),
                "ai_probability": round(signal.ai_probability, 4),
                "edge_bps":       signal.edge_bps,
                "kelly_bps":      signal.kelly_bps,
                "oracle_hash":    signal.oracle_hash,
                "dry_run":        dry_run,
            }

            if dry_run:
                log.info(f"  [DRY RUN] Signal: {json.dumps(signal_record)}")
                signals_logged += 1
            else:
                try:
                    tx_hash = log_position_on_chain(w3, vault, private_key, signal)
                    signal_record["tx_hash"] = tx_hash
                    log.info(f"  ✅ On-chain: https://amoy.polygonscan.com/tx/{tx_hash}")
                    signals_logged += 1
                except Exception as e:
                    log.error(f"  ❌ logPosition() failed: {e}")

        log.info(f"Signals this session: {signals_logged} | Next scan in {SCAN_INTERVAL_SEC}s")
        time.sleep(SCAN_INTERVAL_SEC)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Run in dry-run mode if vault not deployed yet
    vault_deployed = bool(os.getenv("VAULT_CONTRACT_ADDRESS"))
    dry = not vault_deployed

    if dry:
        print("⚠️  VAULT_CONTRACT_ADDRESS not set — running in DRY RUN mode (no on-chain logging)")
        print("   Deploy the vault first: npm run deploy:amoy\n")

    run_agent(dry_run=dry)
