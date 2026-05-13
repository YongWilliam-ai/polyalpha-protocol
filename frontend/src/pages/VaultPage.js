import React, { useState, useEffect, useCallback } from "react";
import { ethers } from "ethers";
import { VAULT_ADDRESS, VAULT_ABI, POLYGONSCAN_URL, CHAIN_ID, CHAIN_NAME, RPC_URL, MOCK_USDC_ADDRESS, USDC_ABI as CONFIG_USDC_ABI } from "../config";
import SocialFeed from "../components/SocialFeed";
import { DataCard } from "../components/DataCard";

const USDC_ABI = CONFIG_USDC_ABI || [
  "function balanceOf(address) view returns (uint256)",
  "function approve(address spender, uint256 amount) returns (bool)",
  "function allowance(address owner, address spender) view returns (uint256)",
  "function decimals() view returns (uint8)",
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

// Demo vault stats for when RPC is unavailable
const DEMO_VAULT_STATS = {
  tvl: 12500.00,
  shares: 12500.0000,
  halted: false,
  drawdown: 3.2,
  peakTvl: 12912.50,
  isDemo: true,
};

export default function VaultPage() {
  const [wallet, setWallet]           = useState(null);
  const [provider, setProvider]       = useState(null);
  const [vaultStats, setVaultStats]   = useState(null);
  const [depositAmt, setDepositAmt]   = useState("");
  const [withdrawAmt, setWithdrawAmt] = useState("");
  const [txStatus, setTxStatus]       = useState("");
  const [loading, setLoading]         = useState(false);
  const [demoMode, setDemoMode]       = useState(false);
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
      setDemoMode(false);
    } catch (e) {
      // Fallback to demo stats if RPC fails
      setVaultStats(DEMO_VAULT_STATS);
      setDemoMode(true);
    }
  }, []);

  useEffect(() => { loadVaultStats(); }, [loadVaultStats]);

  const connectWallet = async () => {
    if (!window.ethereum) {
      show("No wallet detected. Install MetaMask or use a Web3 browser.", "error");
      return;
    }
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
        } catch (switchErr) {
          // If chain doesn't exist, add it
          try {
            await window.ethereum.request({
              method: "wallet_addEthereumChain",
              params: [{
                chainId: "0x" + CHAIN_ID.toString(16),
                chainName: CHAIN_NAME,
                rpcUrls: [RPC_URL],
                nativeCurrency: { name: "ETH", symbol: "ETH", decimals: 18 },
              }],
            });
          } catch {
            show(`Please add ${CHAIN_NAME} (chain ${CHAIN_ID}) to MetaMask manually`, "error");
            return;
          }
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
    // Allow transactions when wallet is connected, even if background RPC read failed (demoMode)
    // demoMode only blocks when there's no wallet provider connected
    setLoading(true);
    setTxStatus("Approving USDC...");
    show("Approving USDC spend...", "info");
    try {
      const signer      = await provider.getSigner();
      const vault       = new ethers.Contract(VAULT_ADDRESS, VAULT_ABI, signer);
      // Try vault.asset() first, fallback to MOCK_USDC_ADDRESS from config
      let usdcAddress;
      try {
        usdcAddress = await vault.asset();
      } catch {
        usdcAddress = MOCK_USDC_ADDRESS;
      }
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
    // Allow transactions when wallet is connected
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
              {vaultStats && !vaultStats.notDeployed && !vaultStats.halted && (
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

          {demoMode && !wallet && (
            <div className="bg-dark border border-yellow-700/30 text-yellow-400 p-3 font-mono text-xs mb-4">
              <span className="font-bold">DEMO MODE</span> — Displaying simulated vault data. Connect your wallet to interact with the live vault on ChainLab Testnet.
            </div>
          )}
          {demoMode && wallet && (
            <div className="bg-dark border border-blue-700/30 text-blue-400 p-3 font-mono text-xs mb-4">
              <span className="font-bold">WALLET CONNECTED</span> — Stats shown are simulated (RPC read failed), but deposits and withdrawals will execute on-chain via MetaMask.
            </div>
          )}

          {/* Hero stats — TVL and APY extra large */}
          {vaultStats && !vaultStats.notDeployed && (
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
                  <rect x="2" y="6" width="20" height="14" rx="2" />
                  <path d="M16 14h.01" />
                  <path d="M2 10h20" />
                </svg>
                Connect Wallet
              </button>
            )}
          </div>

          {/* Deposit / Withdraw */}
          {wallet && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-6">
              <div className="bg-surface border border-gray-800 p-4">
                <div className="text-xs font-mono text-gray-500 uppercase tracking-wider mb-3">// deposit USDC</div>
                <div className="flex gap-2">
                  <input
                    className="bg-dark border border-gray-700 text-gray-200 px-3 py-2 text-sm font-mono focus:outline-none focus:border-accent flex-1"
                    type="number"
                    placeholder="Amount (USDC)"
                    value={depositAmt}
                    onChange={(e) => setDepositAmt(e.target.value)}
                  />
                  <button
                    className="bg-accent hover:bg-accent-dark text-black px-4 py-2 text-sm font-bold transition-colors disabled:opacity-40"
                    onClick={handleDeposit}
                    disabled={loading || !depositAmt}
                  >
                    Deposit
                  </button>
                </div>
              </div>
              <div className="bg-surface border border-gray-800 p-4">
                <div className="text-xs font-mono text-gray-500 uppercase tracking-wider mb-3">// withdraw USDC</div>
                <div className="flex gap-2">
                  <input
                    className="bg-dark border border-gray-700 text-gray-200 px-3 py-2 text-sm font-mono focus:outline-none focus:border-accent flex-1"
                    type="number"
                    placeholder="Amount (USDC)"
                    value={withdrawAmt}
                    onChange={(e) => setWithdrawAmt(e.target.value)}
                  />
                  <button
                    className="border border-gray-700 text-gray-300 hover:border-gray-500 hover:text-white px-4 py-2 text-sm font-bold transition-colors disabled:opacity-40"
                    onClick={handleWithdraw}
                    disabled={loading || !withdrawAmt}
                  >
                    Withdraw
                  </button>
                </div>
              </div>
            </div>
          )}

          {txStatus && (
            <div className="bg-dark border border-gray-800 p-3 font-mono text-xs text-gray-400 mb-4 break-all">
              {txStatus}
            </div>
          )}

          {/* Live Signal Radar */}
          <div className="bg-surface border border-gray-800 p-4">
            <div className="text-xs font-mono text-gray-600 uppercase tracking-wider mb-3">// live_signal_radar</div>
            <div className="grid grid-cols-3 gap-3 text-center">
              <div className="bg-dark border border-gray-800 p-3">
                <div className="text-xs text-gray-500 mb-1">BTC 7-min Δ</div>
                <div className="text-lg font-mono text-success">+0.42%</div>
              </div>
              <div className="bg-dark border border-gray-800 p-3">
                <div className="text-xs text-gray-500 mb-1">Poly Odds (YES)</div>
                <div className="text-lg font-mono text-white">61.2%</div>
              </div>
              <div className="bg-dark border border-gray-800 p-3">
                <div className="text-xs text-gray-500 mb-1">Edge</div>
                <div className="text-lg font-mono text-accent">+13.0%</div>
              </div>
            </div>
            <p className="text-xs text-gray-600 font-mono mt-3">
              Simulated feed · Agent checks every 7 minutes for momentum signals
            </p>
          </div>
        </div>

        {/* ── Right column: Social Feed ── */}
        <div className="hidden lg:block">
          <SocialFeed />
        </div>
      </div>
    </div>
  );
}
