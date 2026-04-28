import React, { useState, useEffect, useCallback } from "react";
import { ethers } from "ethers";
import { VAULT_ADDRESS, VAULT_ABI, POLYGONSCAN_URL, CHAIN_ID, CHAIN_NAME, RPC_URL } from "../config";
import SocialFeed from "../components/SocialFeed";

const USDC_ABI = [
  "function balanceOf(address) view returns (uint256)",
  "function approve(address spender, uint256 amount) returns (bool)",
  "function allowance(address owner, address spender) view returns (uint256)",
];

// ── Toast hook ────────────────────────────────────────────────────────────────
function useToast() {
  const [toasts, setToasts] = useState([]);
  const show = useCallback((message, type = "info") => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 4000);
  }, []);
  return { toasts, show };
}

function ToastStack({ toasts }) {
  if (!toasts.length) return null;
  return (
    <div className="toast-stack">
      {toasts.map((t) => (
        <div key={t.id} className={`toast toast-${t.type}`}>
          {t.message}
        </div>
      ))}
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────────
export default function VaultPage() {
  const [wallet, setWallet]           = useState(null);
  const [provider, setProvider]       = useState(null);
  const [vaultStats, setVaultStats]   = useState(null);
  const [depositAmt, setDepositAmt]   = useState("");
  const [withdrawAmt, setWithdrawAmt] = useState("");
  const [txStatus, setTxStatus]       = useState("");
  const [loading, setLoading]         = useState(false);
  const { toasts, show }              = useToast();

  // Auto-dismiss terminal txStatus after 9 s (leaves time to read + click link)
  useEffect(() => {
    if (!txStatus) return;
    const id = setTimeout(() => setTxStatus(""), 9000);
    return () => clearTimeout(id);
  }, [txStatus]);

  // ── Read vault state (public RPC, no wallet needed) ────────────────────────
  const loadVaultStats = useCallback(async () => {
    if (!VAULT_ADDRESS) { setVaultStats({ notDeployed: true }); return; }
    try {
      const pub   = new ethers.JsonRpcProvider(RPC_URL);
      const vault = new ethers.Contract(VAULT_ADDRESS, VAULT_ABI, pub);
      const [totalAssets, totalShares, halted, drawdownBps, peakAssets] =
        await Promise.all([
          vault.totalAssets(),
          vault.totalSupply(),
          vault.halted(),
          vault.currentDrawdownBps(),
          vault.peakAssets(),
        ]);
      setVaultStats({
        tvl:      Number(totalAssets) / 1e6,
        shares:   Number(totalShares) / 1e6,
        halted,
        drawdown: Number(drawdownBps) / 100,
        peakTvl:  Number(peakAssets) / 1e6,
      });
    } catch (e) {
      setVaultStats({ error: e.message });
    }
  }, []);

  useEffect(() => { loadVaultStats(); }, [loadVaultStats]);

  // ── Connect MetaMask ────────────────────────────────────────────────────────
  const connectWallet = async () => {
    if (!window.ethereum) { show("Install MetaMask to connect", "error"); return; }
    try {
      const accounts = await window.ethereum.request({ method: "eth_requestAccounts" });
      const prov     = new ethers.BrowserProvider(window.ethereum);
      const network  = await prov.getNetwork();
      if (Number(network.chainId) !== CHAIN_ID) {
        try {
          await window.ethereum.request({
            method: "wallet_switchEthereumChain",
            params: [{ chainId: "0x" + CHAIN_ID.toString(16) }],
          });
        } catch {
          show(`Switch MetaMask to ${CHAIN_NAME} (chain ${CHAIN_ID})`, "error");
          return;
        }
      }
      setProvider(prov);
      setWallet(accounts[0]);
      show(`Wallet connected: ${accounts[0].slice(0, 6)}...${accounts[0].slice(-4)}`, "success");
    } catch (e) {
      show("Wallet connection cancelled", "error");
    }
  };

  // ── Deposit ─────────────────────────────────────────────────────────────────
  const handleDeposit = async () => {
    if (!provider || !depositAmt) return;
    setLoading(true);
    setTxStatus("Approving USDC...");
    show("Approving USDC spend...", "info");
    try {
      const signer      = await provider.getSigner();
      const vault       = new ethers.Contract(VAULT_ADDRESS, VAULT_ABI, signer);
      const usdcAddress = await vault.asset();
      const usdc        = new ethers.Contract(usdcAddress, USDC_ABI, signer);
      const amount      = ethers.parseUnits(depositAmt, 6);

      const approveTx = await usdc.approve(VAULT_ADDRESS, amount);
      await approveTx.wait();
      setTxStatus("Depositing...");
      show("Depositing USDC into vault...", "info");

      const depositTx = await vault.deposit(amount, wallet);
      const receipt   = await depositTx.wait();
      setTxStatus(`Deposited! Tx: ${receipt.hash}`);
      show(`Deposited ${depositAmt} USDC successfully`, "success");
      setDepositAmt("");
      loadVaultStats();
    } catch (e) {
      setTxStatus(`Error: ${e.message}`);
      show("Deposit failed — see status below", "error");
    }
    setLoading(false);
  };

  // ── Withdraw ────────────────────────────────────────────────────────────────
  const handleWithdraw = async () => {
    if (!provider || !withdrawAmt) return;
    setLoading(true);
    setTxStatus("Withdrawing...");
    show("Sending withdrawal transaction...", "info");
    try {
      const signer = await provider.getSigner();
      const vault  = new ethers.Contract(VAULT_ADDRESS, VAULT_ABI, signer);
      const amount = ethers.parseUnits(withdrawAmt, 6);
      const tx     = await vault.withdraw(amount, wallet, wallet);
      const receipt = await tx.wait();
      setTxStatus(`Withdrawn! Tx: ${receipt.hash}`);
      show(`Withdrew ${withdrawAmt} USDC successfully`, "success");
      setWithdrawAmt("");
      loadVaultStats();
    } catch (e) {
      setTxStatus(`Error: ${e.message}`);
      show("Withdrawal failed — see status below", "error");
    }
    setLoading(false);
  };

  // ── Early returns ───────────────────────────────────────────────────────────
  if (!VAULT_ADDRESS) {
    return (
      <div className="page">
        <div className="notice warning">
          <strong>Vault not deployed yet.</strong><br />
          Run: <code>npm run deploy:amoy</code> then set <code>REACT_APP_VAULT_ADDRESS</code> in frontend/.env
        </div>
      </div>
    );
  }

  // ── Render ──────────────────────────────────────────────────────────────────
  return (
    <div className="page">
      <ToastStack toasts={toasts} />

      <div className="vault-layout">
        {/* ── Left: vault content ── */}
        <div className="vault-main">
          <div className="page-header">
            <h2>Vault Overview</h2>
            {vaultStats && !vaultStats.notDeployed && !vaultStats.error && (
              <span className={`vault-status-badge ${vaultStats.halted ? "halted" : "live"}`}>
                {vaultStats.halted ? "HALTED" : "LIVE"}
              </span>
            )}
          </div>

          {/* Stats grid */}
          {vaultStats && !vaultStats.notDeployed && !vaultStats.error && (
            <div className="stats-grid">
              <StatCard label="Total Value Locked" value={`$${vaultStats.tvl.toFixed(2)}`} unit="USDC" />
              <StatCard label="Total Shares"        value={vaultStats.shares.toFixed(4)}    unit="paUSDC" />
              <StatCard label="Peak TVL"            value={`$${vaultStats.peakTvl.toFixed(2)}`} unit="USDC" />
              <StatCard
                label="Drawdown from Peak"
                value={`${vaultStats.drawdown.toFixed(1)}%`}
                unit=""
                alert={vaultStats.drawdown > 15}
              />
              <StatCard
                label="Circuit Breaker"
                value={vaultStats.halted ? "HALTED" : "Active"}
                unit=""
                alert={vaultStats.halted}
              />
            </div>
          )}

          {vaultStats?.error && (
            <div className="notice error">
              RPC error — vault stats unavailable: {vaultStats.error}
            </div>
          )}

          {/* Wallet connect */}
          <div className="section">
            <h3>Your Wallet</h3>
            {wallet ? (
              <div className="wallet-connected">
                <span className="wallet-dot" />
                <a
                  className="address"
                  href={`${POLYGONSCAN_URL}/address/${wallet}`}
                  target="_blank"
                  rel="noreferrer"
                >
                  {wallet.slice(0, 6)}...{wallet.slice(-4)}
                </a>
                <span className="chain-badge">{CHAIN_NAME}</span>
              </div>
            ) : (
              <button className="btn-primary connect-btn" onClick={connectWallet}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ marginRight: 6 }}>
                  <rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
                </svg>
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
                  {loading ? "Processing..." : "Deposit"}
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
                  {loading ? "Processing..." : "Withdraw"}
                </button>
              </div>

              {txStatus && (
                <div className={`notice ${
                  txStatus.startsWith("Deposited") || txStatus.startsWith("Withdrawn")
                    ? "success"
                    : txStatus.startsWith("Error")
                    ? "error"
                    : "info"
                }`}>
                  {txStatus}
                  {txStatus.includes("Tx:") && (
                    <>
                      {" "}
                      <a
                        href={`${POLYGONSCAN_URL}/tx/${txStatus.split("Tx: ")[1]}`}
                        target="_blank"
                        rel="noreferrer"
                      >
                        View on Explorer
                      </a>
                    </>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Risk parameters */}
          <div className="section">
            <h3>Risk Parameters</h3>
            <table className="params-table">
              <tbody>
                <tr><td>Performance Fee</td>   <td>20% of profits</td></tr>
                <tr><td>Management Fee</td>    <td>0.5% annual</td></tr>
                <tr><td>Max Position Size</td> <td>5% of TVL per trade</td></tr>
                <tr><td>Max Total Exposure</td><td>40% of TVL</td></tr>
                <tr><td>Circuit Breaker</td>   <td>Auto-halt at 20% drawdown from peak</td></tr>
                <tr><td>Kelly Fraction</td>    <td>Quarter-Kelly (25% of full Kelly)</td></tr>
              </tbody>
            </table>
            <p className="caption">
              Hardcoded in <code>PolyAlphaVault.sol</code>.
              Phase 2: DAO governance controls risk parameters via 48h timelock.
            </p>
          </div>
        </div>

        {/* ── Right: social feed ── */}
        <div className="vault-sidebar">
          <SocialFeed />
        </div>
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
