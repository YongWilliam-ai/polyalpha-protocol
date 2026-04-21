import React, { useState, useEffect, useCallback } from "react";
import { ethers } from "ethers";
import { VAULT_ADDRESS, VAULT_ABI, POLYGONSCAN_URL, CHAIN_ID, CHAIN_NAME, RPC_URL } from "../config";

const USDC_ABI = [
  "function balanceOf(address) view returns (uint256)",
  "function approve(address spender, uint256 amount) returns (bool)",
  "function allowance(address owner, address spender) view returns (uint256)",
];

export default function VaultPage() {
  const [wallet, setWallet]         = useState(null);
  const [provider, setProvider]     = useState(null);
  const [vaultStats, setVaultStats] = useState(null);
  const [depositAmt, setDepositAmt] = useState("");
  const [withdrawAmt, setWithdrawAmt] = useState("");
  const [txStatus, setTxStatus]     = useState("");
  const [loading, setLoading]       = useState(false);

  // ── Read vault state (public RPC, no wallet needed) ────────────────────────
  const loadVaultStats = useCallback(async () => {
    if (!VAULT_ADDRESS) {
      setVaultStats({ notDeployed: true });
      return;
    }
    try {
      const pub = new ethers.JsonRpcProvider(RPC_URL);
      const vault = new ethers.Contract(VAULT_ADDRESS, VAULT_ABI, pub);
      const [totalAssets, totalShares, halted, drawdownBps, peakAssets] = await Promise.all([
        vault.totalAssets(),
        vault.totalSupply(),
        vault.halted(),
        vault.currentDrawdownBps(),
        vault.peakAssets(),
      ]);
      setVaultStats({
        tvl:          Number(totalAssets) / 1e6,
        shares:       Number(totalShares) / 1e6,
        halted,
        drawdown:     Number(drawdownBps) / 100,
        peakTvl:      Number(peakAssets) / 1e6,
      });
    } catch (e) {
      setVaultStats({ error: e.message });
    }
  }, []);

  useEffect(() => { loadVaultStats(); }, [loadVaultStats]);

  // ── Connect MetaMask ────────────────────────────────────────────────────────
  const connectWallet = async () => {
    if (!window.ethereum) { alert("Install MetaMask first"); return; }
    try {
      const accounts = await window.ethereum.request({ method: "eth_requestAccounts" });
      const prov = new ethers.BrowserProvider(window.ethereum);
      const network = await prov.getNetwork();
      if (Number(network.chainId) !== CHAIN_ID) {
        try {
          await window.ethereum.request({
            method: "wallet_switchEthereumChain",
            params: [{ chainId: "0x" + CHAIN_ID.toString(16) }],
          });
        } catch {
          alert(`Please switch MetaMask to ${CHAIN_NAME} (chain ID ${CHAIN_ID})`);
          return;
        }
      }
      setProvider(prov);
      setWallet(accounts[0]);
    } catch (e) {
      console.error(e);
    }
  };

  // ── Deposit ─────────────────────────────────────────────────────────────────
  const handleDeposit = async () => {
    if (!provider || !depositAmt) return;
    setLoading(true);
    setTxStatus("Approving USDC...");
    try {
      const signer = await provider.getSigner();
      const vault = new ethers.Contract(VAULT_ADDRESS, VAULT_ABI, signer);
      const usdcAddress = await vault.asset();
      const usdc = new ethers.Contract(usdcAddress, USDC_ABI, signer);
      const amount = ethers.parseUnits(depositAmt, 6);

      const approveTx = await usdc.approve(VAULT_ADDRESS, amount);
      await approveTx.wait();
      setTxStatus("Depositing...");

      const depositTx = await vault.deposit(amount, wallet);
      const receipt = await depositTx.wait();
      setTxStatus(`✅ Deposited! Tx: ${receipt.hash}`);
      setDepositAmt("");
      loadVaultStats();
    } catch (e) {
      setTxStatus(`❌ ${e.message}`);
    }
    setLoading(false);
  };

  // ── Withdraw ────────────────────────────────────────────────────────────────
  const handleWithdraw = async () => {
    if (!provider || !withdrawAmt) return;
    setLoading(true);
    setTxStatus("Withdrawing...");
    try {
      const signer = await provider.getSigner();
      const vault = new ethers.Contract(VAULT_ADDRESS, VAULT_ABI, signer);
      const amount = ethers.parseUnits(withdrawAmt, 6);
      const tx = await vault.withdraw(amount, wallet, wallet);
      const receipt = await tx.wait();
      setTxStatus(`✅ Withdrawn! Tx: ${receipt.hash}`);
      setWithdrawAmt("");
      loadVaultStats();
    } catch (e) {
      setTxStatus(`❌ ${e.message}`);
    }
    setLoading(false);
  };

  // ── Render ──────────────────────────────────────────────────────────────────
  if (!VAULT_ADDRESS) {
    return (
      <div className="page">
        <div className="notice warning">
          <strong>⚠️ Vault not deployed yet.</strong><br />
          Run: <code>npm run deploy:amoy</code> then set <code>REACT_APP_VAULT_ADDRESS</code> in frontend/.env
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <h2>Vault Overview</h2>

      {/* Stats grid */}
      {vaultStats && !vaultStats.notDeployed && !vaultStats.error && (
        <div className="stats-grid">
          <StatCard label="Total Value Locked" value={`$${vaultStats.tvl.toFixed(2)}`} unit="USDC" />
          <StatCard label="Total Shares" value={vaultStats.shares.toFixed(4)} unit="paUSDC" />
          <StatCard label="Peak TVL" value={`$${vaultStats.peakTvl.toFixed(2)}`} unit="USDC" />
          <StatCard
            label="Drawdown from Peak"
            value={`${vaultStats.drawdown.toFixed(1)}%`}
            unit=""
            alert={vaultStats.drawdown > 15}
          />
          <StatCard
            label="Circuit Breaker"
            value={vaultStats.halted ? "🔴 HALTED" : "🟢 Active"}
            unit=""
            alert={vaultStats.halted}
          />
        </div>
      )}

      {vaultStats?.error && (
        <div className="notice error">Failed to load vault: {vaultStats.error}</div>
      )}

      {/* Wallet connect */}
      <div className="section">
        <h3>Your Wallet</h3>
        {wallet ? (
          <p className="address">
            Connected: <a href={`${POLYGONSCAN_URL}/address/${wallet}`} target="_blank" rel="noreferrer">
              {wallet.slice(0, 6)}...{wallet.slice(-4)}
            </a>
          </p>
        ) : (
          <button className="btn-primary" onClick={connectWallet}>
            Connect MetaMask
          </button>
        )}
      </div>

      {/* Deposit / Withdraw */}
      {wallet && (
        <div className="section">
          <h3>Deposit / Withdraw USDC</h3>
          <div className="form-row">
            <input
              type="number"
              placeholder="Amount (USDC)"
              value={depositAmt}
              onChange={(e) => setDepositAmt(e.target.value)}
              className="input"
            />
            <button className="btn-primary" onClick={handleDeposit} disabled={loading}>
              Deposit
            </button>
          </div>
          <div className="form-row" style={{ marginTop: "0.5rem" }}>
            <input
              type="number"
              placeholder="Amount (USDC)"
              value={withdrawAmt}
              onChange={(e) => setWithdrawAmt(e.target.value)}
              className="input"
            />
            <button className="btn-outline" onClick={handleWithdraw} disabled={loading}>
              Withdraw
            </button>
          </div>
          {txStatus && (
            <div className={`notice ${txStatus.startsWith("✅") ? "success" : txStatus.startsWith("❌") ? "error" : "info"}`}>
              {txStatus}
              {txStatus.includes("Tx:") && (
                <>
                  {" "}
                  <a
                    href={`${POLYGONSCAN_URL}/tx/${txStatus.split("Tx: ")[1]}`}
                    target="_blank" rel="noreferrer"
                  >
                    View on Polygonscan →
                  </a>
                </>
              )}
            </div>
          )}
        </div>
      )}

      {/* Risk parameters */}
      <div className="section">
        <h3>Risk Parameters (Hardcoded)</h3>
        <table className="params-table">
          <tbody>
            <tr><td>Performance Fee</td><td>20% of profits</td></tr>
            <tr><td>Management Fee</td><td>0.5% annual</td></tr>
            <tr><td>Max Position Size</td><td>5% of TVL per trade</td></tr>
            <tr><td>Max Total Exposure</td><td>40% of TVL</td></tr>
            <tr><td>Circuit Breaker</td><td>Auto-halt at 20% drawdown from peak</td></tr>
            <tr><td>Kelly Fraction</td><td>Quarter-Kelly (25% of full Kelly)</td></tr>
          </tbody>
        </table>
        <p className="caption">
          All parameters are hardcoded in <code>PolyAlphaVault.sol</code>.
          Phase 2: DAO governance controls risk parameters via 48h timelock.
        </p>
      </div>
    </div>
  );
}

function StatCard({ label, value, unit, alert }) {
  return (
    <div className={`stat-card ${alert ? "stat-alert" : ""}`}>
      <div className="stat-label">{label}</div>
      <div className="stat-value">{value}</div>
      {unit && <div className="stat-unit">{unit}</div>}
    </div>
  );
}
