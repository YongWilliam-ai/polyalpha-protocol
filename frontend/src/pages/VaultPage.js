import React, { useState, useEffect, useCallback } from "react";
import { ethers } from "ethers";
import { VAULT_ADDRESS, VAULT_ABI, POLYGONSCAN_URL, CHAIN_ID, CHAIN_NAME, RPC_URL } from "../config";
import SocialFeed from "../components/SocialFeed";
import { DataCard } from "../components/DataCard";

const USDC_ABI = [
  "function balanceOf(address) view returns (uint256)",
  "function approve(address spender, uint256 amount) returns (bool)",
  "function allowance(address owner, address spender) view returns (uint256)",
];

function useToast() {
  const [toasts, setToasts] = useState([]);
  const show = useCallback((message, type = "info") => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 4000);
  }, []);
  return { toasts, show };
}

const TOAST_CLS = {
  info:    "bg-surface border border-gray-700 text-gray-300",
  success: "bg-dark border border-success/30 text-success",
  error:   "bg-dark border border-red-500/30 text-red-300",
};

function ToastStack({ toasts }) {
  if (!toasts.length) return null;
  return (
    <div className="fixed top-4 right-4 z-[9999] flex flex-col gap-2 pointer-events-none">
      {toasts.map((t) => (
        <div
          key={t.id}
          className={`px-4 py-3 text-sm font-mono min-w-[220px] max-w-sm shadow-xl ${TOAST_CLS[t.type] || TOAST_CLS.info}`}
          style={{ animation: "toast-in 0.2s ease" }}
        >
          {t.message}
        </div>
      ))}
    </div>
  );
}

export default function VaultPage() {
  const [wallet, setWallet]           = useState(null);
  const [provider, setProvider]       = useState(null);
  const [vaultStats, setVaultStats]   = useState(null);
  const [depositAmt, setDepositAmt]   = useState("");
  const [withdrawAmt, setWithdrawAmt] = useState("");
  const [txStatus, setTxStatus]       = useState("");
  const [loading, setLoading]         = useState(false);
  const { toasts, show }              = useToast();

  useEffect(() => {
    if (!txStatus) return;
    const id = setTimeout(() => setTxStatus(""), 9000);
    return () => clearTimeout(id);
  }, [txStatus]);

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
      show(`Connected: ${accounts[0].slice(0, 6)}...${accounts[0].slice(-4)}`, "success");
    } catch {
      show("Wallet connection cancelled", "error");
    }
  };

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
      await (await usdc.approve(VAULT_ADDRESS, amount)).wait();
      setTxStatus("Depositing...");
      show("Depositing USDC into vault...", "info");
      const receipt = await (await vault.deposit(amount, wallet)).wait();
      setTxStatus(`Deposited! Tx: ${receipt.hash}`);
      show(`Deposited ${depositAmt} USDC`, "success");
      setDepositAmt(""); loadVaultStats();
    } catch (e) {
      setTxStatus(`Error: ${e.message}`);
      show("Deposit failed", "error");
    }
    setLoading(false);
  };

  const handleWithdraw = async () => {
    if (!provider || !withdrawAmt) return;
    setLoading(true);
    setTxStatus("Withdrawing...");
    show("Sending withdrawal...", "info");
    try {
      const signer  = await provider.getSigner();
      const vault   = new ethers.Contract(VAULT_ADDRESS, VAULT_ABI, signer);
      const amount  = ethers.parseUnits(withdrawAmt, 6);
      const receipt = await (await vault.withdraw(amount, wallet, wallet)).wait();
      setTxStatus(`Withdrawn! Tx: ${receipt.hash}`);
      show(`Withdrew ${withdrawAmt} USDC`, "success");
      setWithdrawAmt(""); loadVaultStats();
    } catch (e) {
      setTxStatus(`Error: ${e.message}`);
      show("Withdrawal failed", "error");
    }
    setLoading(false);
  };

  if (!VAULT_ADDRESS) {
    return (
      <div className="bg-dark border border-yellow-700/30 text-yellow-400 p-4 font-mono text-sm">
        <strong>Vault not deployed.</strong> Run:{" "}
        <code className="text-accent">npm run deploy:amoy</code> then set{" "}
        <code className="text-accent">REACT_APP_VAULT_ADDRESS</code> in frontend/.env
      </div>
    );
  }

  return (
    <div>
      <ToastStack toasts={toasts} />

      <div className="grid grid-cols-1 lg:grid-cols-[1fr_340px] gap-6 items-start">
        {/* ── Left column ── */}
        <div className="min-w-0">

          {/* Hero block */}
          <div className="mb-6">
            <div className="flex items-center gap-3 mb-1 flex-wrap">
              <h1 className="text-3xl font-bold text-white tracking-tight">PolyAlpha Vault</h1>
              {vaultStats && !vaultStats.notDeployed && !vaultStats.error && !vaultStats.halted && (
                <span className="flex items-center gap-2">
                  <span className="flex h-3 w-3 relative">
                    <span className="animate-ping absolute inline-flex h-full w-full bg-success opacity-75" />
                    <span className="relative inline-flex h-3 w-3 bg-success" />
                  </span>
                  <span className="text-xs font-mono text-success uppercase tracking-widest">LIVE</span>
                </span>
              )}
              {vaultStats?.halted && (
                <span className="text-xs font-mono text-red-400 border border-red-500/40 px-2 py-0.5 uppercase tracking-widest">
                  HALTED
                </span>
              )}
            </div>
            <p className="text-gray-500 font-mono text-xs">
              ERC-4626 · Agent-Native Prediction Market Arbitrage · Quarter-Kelly Sizing
            </p>
          </div>

          {/* Hero stats — TVL and APY extra large */}
          {vaultStats && !vaultStats.notDeployed && !vaultStats.error && (
            <>
              {/* Primary metrics — massive numbers */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
                <div className="bg-surface border border-gray-800 border-t-2 border-t-accent p-6 edge-glow hover:bg-surface-hover transition-all duration-300 group">
                  <div className="text-xs font-mono text-gray-500 uppercase tracking-wider mb-2">Total Value Locked</div>
                  <div className="text-6xl font-mono font-bold text-white group-hover:text-accent transition-colors leading-none">
                    ${vaultStats.tvl.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </div>
                  <div className="text-xs font-mono text-gray-600 mt-2">USDC</div>
                </div>
                <div className="bg-surface border border-gray-800 border-t-2 border-t-accent p-6 edge-glow hover:bg-surface-hover transition-all duration-300 group">
                  <div className="text-xs font-mono text-gray-500 uppercase tracking-wider mb-2">Target APY (Staking)</div>
                  <div className="text-6xl font-mono font-bold text-accent leading-none">
                    10%
                  </div>
                  <div className="text-xs font-mono text-gray-600 mt-2">Synthetix-style 10% fixed · PALPHA stakers</div>
                </div>
              </div>

              {/* Secondary metrics */}
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-6">
                <DataCard label="Total Shares"       value={vaultStats.shares.toFixed(4)}         unit="paUSDC" />
                <DataCard label="Peak TVL"           value={`$${vaultStats.peakTvl.toFixed(2)}`} unit="USDC"   />
                <DataCard label="Drawdown from Peak" value={`${vaultStats.drawdown.toFixed(1)}%`} alert={vaultStats.drawdown > 15} />
                <DataCard label="Circuit Breaker"    value={vaultStats.halted ? "HALTED" : "Active"} alert={vaultStats.halted} />
                <DataCard label="Max Position"       value="5% TVL"  unit="per trade" />
                <DataCard label="Kelly Fraction"     value="0.25x"   unit="Quarter-Kelly" />
              </div>
            </>
          )}

          {vaultStats?.error && (
            <div className="bg-dark border border-red-500/30 text-red-400 p-4 font-mono text-sm mb-4">
              <span className="text-red-600">RPC ERR</span> vault stats unavailable: {vaultStats.error}
            </div>
          )}

          {/* Wallet connect */}
          <div className="mb-6">
            <div className="text-xs font-mono text-gray-600 uppercase tracking-wider mb-3">// wallet</div>
            {wallet ? (
              <div className="flex items-center gap-3">
                <span className="w-2 h-2 bg-success shadow-[0_0_6px_#00E676]" />
                <a
                  className="font-mono text-sm text-accent hover:underline"
                  href={`${POLYGONSCAN_URL}/address/${wallet}`}
                  target="_blank"
                  rel="noreferrer"
                >
                  {wallet.slice(0, 6)}...{wallet.slice(-4)}
                </a>
                <span className="text-xs bg-gray-900 text-gray-400 px-2 py-0.5 font-mono border border-gray-800">{CHAIN_NAME}</span>
              </div>
            ) : (
              <button
                className="flex items-center gap-2 bg-accent hover:bg-accent-dark text-black px-5 py-2.5 text-sm font-bold transition-colors"
                onClick={connectWallet}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="2" y="7" width="20" height="14" rx="2"/>
                  <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
                </svg>
                Connect MetaMask
              </button>
            )}
          </div>

          {/* Deposit / Withdraw */}
          {wallet && (
            <div className="mb-6">
              <div className="text-xs font-mono text-gray-600 uppercase tracking-wider mb-3">// deposit / withdraw</div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="bg-surface border border-gray-800 p-4">
                  <div className="text-xs font-mono text-gray-600 mb-2">DEPOSIT USDC</div>
                  <div className="flex gap-2">
                    <input
                      type="number"
                      placeholder="0.00"
                      value={depositAmt}
                      onChange={(e) => setDepositAmt(e.target.value)}
                      className="bg-dark border border-gray-700 text-gray-200 px-3 py-2 font-mono text-sm focus:outline-none focus:border-accent flex-1 min-w-0"
                    />
                    <button
                      className="bg-accent hover:bg-accent-dark text-black px-4 py-2 text-sm font-bold transition-colors disabled:opacity-50"
                      onClick={handleDeposit}
                      disabled={loading}
                    >
                      {loading ? "..." : "Deposit"}
                    </button>
                  </div>
                </div>
                <div className="bg-surface border border-gray-800 p-4">
                  <div className="text-xs font-mono text-gray-600 mb-2">WITHDRAW USDC</div>
                  <div className="flex gap-2">
                    <input
                      type="number"
                      placeholder="0.00"
                      value={withdrawAmt}
                      onChange={(e) => setWithdrawAmt(e.target.value)}
                      className="bg-dark border border-gray-700 text-gray-200 px-3 py-2 font-mono text-sm focus:outline-none focus:border-accent flex-1 min-w-0"
                    />
                    <button
                      className="border border-accent text-accent hover:bg-accent/10 px-4 py-2 text-sm font-bold transition-colors disabled:opacity-50"
                      onClick={handleWithdraw}
                      disabled={loading}
                    >
                      {loading ? "..." : "Withdraw"}
                    </button>
                  </div>
                </div>
              </div>

              {txStatus && (
                <div className={`mt-3 p-3 text-sm font-mono ${
                  txStatus.startsWith("Deposited") || txStatus.startsWith("Withdrawn")
                    ? "bg-dark border border-success/30 text-success"
                    : txStatus.startsWith("Error")
                    ? "bg-dark border border-red-500/30 text-red-400"
                    : "bg-surface border border-gray-700 text-gray-300"
                }`}>
                  {txStatus}
                  {txStatus.includes("Tx:") && (
                    <a
                      href={`${POLYGONSCAN_URL}/tx/${txStatus.split("Tx: ")[1]}`}
                      target="_blank"
                      rel="noreferrer"
                      className="ml-2 text-accent hover:underline"
                    >
                      View on Explorer
                    </a>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Risk Parameters */}
          <div>
            <div className="text-xs font-mono text-gray-600 uppercase tracking-wider mb-3">// risk_parameters</div>
            <div className="bg-surface border border-gray-800 overflow-hidden">
              <table className="w-full text-sm">
                <tbody>
                  {[
                    ["performance_fee",      "20% of profits"],
                    ["management_fee",       "0.5% annual"],
                    ["max_position_size",    "5% of TVL per trade"],
                    ["max_total_exposure",   "40% of TVL"],
                    ["circuit_breaker",      "auto-halt at 20% drawdown from peak"],
                    ["kelly_fraction",       "0.25x (Quarter-Kelly)"],
                  ].map(([param, val]) => (
                    <tr key={param} className="border-b border-gray-800 last:border-0 hover:bg-surface-hover transition-colors">
                      <td className="px-4 py-3 text-xs font-mono text-gray-600">{param}</td>
                      <td className="px-4 py-3 text-sm font-mono text-white">{val}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="text-xs text-gray-700 font-mono mt-2">
              hardcoded in PolyAlphaVault.sol · Phase 2: DAO governance via 48h timelock
            </p>
          </div>
        </div>

        {/* ── Right column ── */}
        <div className="lg:sticky lg:top-20">
          <SocialFeed />
        </div>
      </div>
    </div>
  );
}
