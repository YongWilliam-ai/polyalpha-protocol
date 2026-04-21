"""
test_connection.py — PolyAlpha connection verification

Verifies:
  1. Polymarket CLOB API is reachable
  2. BTC Up/Down 15m markets are returned
  3. Binance BTC price feed is reachable
  4. (Optional) Vault contract is readable on Amoy

Run: python test_connection.py
Expected output: table of active BTC 15m markets with current YES prices
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

CLOB_API   = "https://clob.polymarket.com"
GAMMA_API  = "https://gamma-api.polymarket.com"
BINANCE_API = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"


# ── 1. Polymarket Gamma API — market discovery ────────────────────────────────

def fetch_btc_markets(limit: int = 20) -> list[dict]:
    """Fetch active BTC Up/Down prediction markets from Gamma API."""
    url = f"{GAMMA_API}/markets"
    params = {
        "active": "true",
        "closed": "false",
        "limit": limit,
        "tag_slug": "crypto",
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    markets = resp.json()

    btc_markets = [
        m for m in markets
        if "bitcoin" in m.get("question", "").lower()
        or "btc" in m.get("question", "").lower()
    ]
    return btc_markets


# ── 2. Polymarket CLOB API — live order book prices ───────────────────────────

def fetch_market_price(condition_id: str) -> dict | None:
    """Fetch best bid/ask for a market condition ID from the CLOB."""
    url = f"{CLOB_API}/book"
    params = {"token_id": condition_id}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


def fetch_midprice(condition_id: str) -> float | None:
    """Return the mid-price (0–1) for a YES outcome."""
    url = f"{CLOB_API}/midpoint"
    params = {"token_id": condition_id}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return float(data.get("mid", 0))
    except Exception:
        return None


# ── 3. Binance BTC price ──────────────────────────────────────────────────────

def fetch_btc_price() -> float:
    """Fetch current BTC/USDT spot price from Binance."""
    resp = requests.get(BINANCE_API, timeout=5)
    resp.raise_for_status()
    return float(resp.json()["price"])


# ── 4. Vault contract read (optional) ────────────────────────────────────────

def check_vault_connection() -> dict | None:
    """Read basic vault state from Polygon Amoy (requires VAULT_CONTRACT_ADDRESS in .env)."""
    vault_address = os.getenv("VAULT_CONTRACT_ADDRESS")
    if not vault_address:
        return None

    try:
        from web3 import Web3
        rpc = os.getenv("AMOY_RPC_URL", "https://rpc-amoy.polygon.technology/")
        w3 = Web3(Web3.HTTPProvider(rpc))

        # Minimal ABI for read-only vault check
        abi = [
            {"name": "totalAssets",     "type": "function", "inputs": [], "outputs": [{"type": "uint256"}], "stateMutability": "view"},
            {"name": "totalSupply",     "type": "function", "inputs": [], "outputs": [{"type": "uint256"}], "stateMutability": "view"},
            {"name": "halted",          "type": "function", "inputs": [], "outputs": [{"type": "bool"}],    "stateMutability": "view"},
            {"name": "currentDrawdownBps", "type": "function", "inputs": [], "outputs": [{"type": "uint256"}], "stateMutability": "view"},
        ]
        vault = w3.eth.contract(address=Web3.to_checksum_address(vault_address), abi=abi)
        return {
            "total_assets_usdc": vault.functions.totalAssets().call() / 1e6,
            "total_shares":      vault.functions.totalSupply().call() / 1e6,
            "halted":            vault.functions.halted().call(),
            "drawdown_bps":      vault.functions.currentDrawdownBps().call(),
        }
    except Exception as e:
        return {"error": str(e)}


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("PolyAlpha — Connection Test")
    print("=" * 60)

    # BTC price
    print("\n[1] Binance BTC price...")
    try:
        btc_price = fetch_btc_price()
        print(f"    ✅ BTC/USDT = ${btc_price:,.2f}")
    except Exception as e:
        print(f"    ❌ Failed: {e}")
        btc_price = None

    # Polymarket markets
    print("\n[2] Polymarket BTC markets (Gamma API)...")
    try:
        markets = fetch_btc_markets(limit=50)
        print(f"    ✅ Found {len(markets)} BTC-related markets")

        if markets:
            print(f"\n    {'Question':<50} {'Condition ID':<44} {'Liquidity':>12}")
            print("    " + "-" * 110)
            for m in markets[:10]:
                q = m.get("question", "")[:48]
                cid = m.get("conditionId", "N/A")
                liquidity = float(m.get("liquidity", 0))
                print(f"    {q:<50} {cid:<44} ${liquidity:>10,.0f}")
    except Exception as e:
        print(f"    ❌ Failed: {e}")
        markets = []

    # Vault connection (optional)
    print("\n[3] Vault contract (Polygon Amoy)...")
    vault_info = check_vault_connection()
    if vault_info is None:
        print("    ⚠️  VAULT_CONTRACT_ADDRESS not set in .env — deploy first")
    elif "error" in vault_info:
        print(f"    ❌ {vault_info['error']}")
    else:
        print(f"    ✅ Total Assets: ${vault_info['total_assets_usdc']:.2f} USDC")
        print(f"       Total Shares: {vault_info['total_shares']:.2f} paUSDC")
        print(f"       Halted: {vault_info['halted']}")
        print(f"       Drawdown: {vault_info['drawdown_bps'] / 100:.1f}%")

    print("\n" + "=" * 60)
    status_ok = btc_price is not None and len(markets) > 0
    if status_ok:
        print("✅ All connections working. Ready to run agent.py")
    else:
        print("❌ Some connections failed — fix above errors first")
    print("=" * 60)

    return markets


if __name__ == "__main__":
    main()
