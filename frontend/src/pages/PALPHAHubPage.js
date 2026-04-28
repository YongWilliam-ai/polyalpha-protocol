import React, { useState, useEffect, useCallback } from "react";
import { ethers } from "ethers";
import {
  STAKING_ADDRESS, STAKING_ABI,
  BUYBACK_ADDRESS, BUYBACK_ABI,
  PALPHA_ADDRESS,  PALPHA_ABI,
  DAO_ADDRESS,     DAO_ABI,
} from "../config";

// ── Helpers ───────────────────────────────────────────────────────────────────

function fmt(wei, decimals = 18) {
  if (wei === null || wei === undefined) return "—";
  try {
    return parseFloat(ethers.formatUnits(wei, decimals)).toLocaleString(undefined, { maximumFractionDigits: 2 });
  } catch { return "—"; }
}

function shortAddr(addr) {
  if (!addr) return "—";
  return addr.slice(0, 6) + "..." + addr.slice(-4);
}

function timeLeft(deadline) {
  const now  = Math.floor(Date.now() / 1000);
  const diff = Number(deadline) - now;
  if (diff <= 0) return "Closed";
  const h = Math.floor(diff / 3600);
  const m = Math.floor((diff % 3600) / 60);
  return h + "h " + m + "m left";
}

// ── Shared card wrapper ───────────────────────────────────────────────────────

function SectionCard({ children }) {
  return (
    <div className="bg-surface border border-gray-800 rounded-lg p-6">
      {children}
    </div>
  );
}

// ── Staking ───────────────────────────────────────────────────────────────────

function StakingSection({ provider, signer, address }) {
  const [data,   setData]   = useState({ staked: null, earned: null, total: null });
  const [amount, setAmount] = useState("");
  const [status, setStatus] = useState("");

  const load = useCallback(async () => {
    if (!provider || !address) return;
    try {
      const staking = new ethers.Contract(STAKING_ADDRESS, STAKING_ABI, provider);
      const [staked, earned, total] = await Promise.all([
        staking.stakedBalance(address),
        staking.earned(address),
        staking.totalStaked(),
      ]);
      setData({ staked, earned, total });
    } catch (e) { console.error("Staking load:", e); }
  }, [provider, address]);

  useEffect(() => { load(); }, [load]);

  async function approve(amountWei) {
    const palpha = new ethers.Contract(PALPHA_ADDRESS, PALPHA_ABI, signer);
    await (await palpha.approve(STAKING_ADDRESS, amountWei)).wait();
  }

  async function handleStake() {
    try {
      setStatus("Approving...");
      const amountWei = ethers.parseEther(amount);
      await approve(amountWei);
      setStatus("Staking...");
      const staking = new ethers.Contract(STAKING_ADDRESS, STAKING_ABI, signer);
      await (await staking.stake(amountWei)).wait();
      setStatus("Staked!"); setAmount(""); load();
    } catch (e) { setStatus("Error: " + (e.reason || e.message)); }
  }

  async function handleUnstake() {
    try {
      setStatus("Unstaking...");
      const amountWei = ethers.parseEther(amount);
      const staking = new ethers.Contract(STAKING_ADDRESS, STAKING_ABI, signer);
      await (await staking.unstake(amountWei)).wait();
      setStatus("Unstaked!"); setAmount(""); load();
    } catch (e) { setStatus("Error: " + (e.reason || e.message)); }
  }

  async function handleClaim() {
    try {
      setStatus("Claiming...");
      const staking = new ethers.Contract(STAKING_ADDRESS, STAKING_ABI, signer);
      await (await staking.claimReward()).wait();
      setStatus("Claimed!"); load();
    } catch (e) { setStatus("Error: " + (e.reason || e.message)); }
  }

  return (
    <SectionCard>
      <h2 className="text-lg font-bold text-white mb-4">PALPHA Staking</h2>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-5">
        {[
          { label: "Your Staked",       value: fmt(data.staked) + " PALPHA" },
          { label: "Earned Rewards",    value: fmt(data.earned) + " PALPHA" },
          { label: "Total Pool Staked", value: fmt(data.total)  + " PALPHA" },
        ].map(({ label, value }) => (
          <div key={label} className="bg-dark border border-gray-800 rounded-lg p-4">
            <div className="text-xs font-mono text-gray-500 uppercase tracking-wider mb-1">{label}</div>
            <div className="text-lg font-mono font-semibold text-white">{value}</div>
          </div>
        ))}
      </div>

      {signer ? (
        <div className="flex flex-wrap items-center gap-2">
          <input
            className="bg-dark border border-gray-700 text-gray-200 px-3 py-2 rounded-lg text-sm focus:outline-none focus:border-accent flex-1 min-w-[160px]"
            type="number"
            placeholder="Amount (PALPHA)"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
          />
          <button
            className="bg-accent hover:bg-orange-600 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors"
            onClick={handleStake}
          >
            Stake
          </button>
          <button
            className="border border-gray-700 text-gray-300 hover:border-gray-500 hover:text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors"
            onClick={handleUnstake}
          >
            Unstake
          </button>
          <button
            className="border border-success/40 text-success hover:bg-success/10 px-4 py-2 rounded-lg text-sm font-semibold transition-colors"
            onClick={handleClaim}
          >
            Claim Rewards
          </button>
        </div>
      ) : (
        <p className="text-sm text-gray-500 font-mono">Connect wallet to stake</p>
      )}
      {status && <p className="mt-3 text-sm font-mono text-accent">{status}</p>}
    </SectionCard>
  );
}

// ── Governance ────────────────────────────────────────────────────────────────

const MOCK_PROPOSALS = [
  {
    id: 0,
    proposer:       "0xfEe9eeC07f9f689aA2F81e240f3199E02f93896d",
    description:    "Increase vault max drawdown circuit breaker from 20% to 25% to allow longer trend trades.",
    forVotes:       ethers.parseEther("320000"),
    againstVotes:   ethers.parseEther("80000"),
    executed:       true,
    canceled:       false,
    votingDeadline: BigInt(Math.floor(Date.now() / 1000) - 86400),
  },
  {
    id: 1,
    proposer:       "0xfEe9eeC07f9f689aA2F81e240f3199E02f93896d",
    description:    "Allocate 5% of buyback revenue to a community grants multisig for ecosystem development.",
    forVotes:       ethers.parseEther("150000"),
    againstVotes:   ethers.parseEther("20000"),
    executed:       false,
    canceled:       false,
    votingDeadline: BigInt(Math.floor(Date.now() / 1000) + 3600 * 36),
  },
];

function GovernanceSection({ provider, signer, address }) {
  const [proposals,      setProposals]     = useState(MOCK_PROPOSALS);
  const [usingCachedData, setUsingCached]  = useState(true);
  const [loading,        setLoading]       = useState(false);
  const [liveCount,      setLiveCount]     = useState(null);
  const [showForm,       setShowForm]      = useState(false);
  const [form,           setForm]          = useState({ description: "", target: "", callData: "0x" });
  const [status,         setStatus]        = useState("");

  const fetchProposals = useCallback(async () => {
    if (!provider) return;
    setLoading(true);
    try {
      const dao   = new ethers.Contract(DAO_ADDRESS, DAO_ABI, provider);
      const count = await dao.proposalCount();
      const n     = Number(count);
      setLiveCount(n);
      if (n === 0) { setProposals(MOCK_PROPOSALS); setUsingCached(true); return; }
      const fetched = await Promise.all(
        Array.from({ length: n }, (_, i) =>
          dao.getProposal(i).then((p) => ({
            id: i, proposer: p[0], description: p[1], targetContract: p[2],
            createdAt: p[3], votingDeadline: p[4],
            forVotes: p[5], againstVotes: p[6], executed: p[7], canceled: p[8],
          }))
        )
      );
      setProposals(fetched);
      setUsingCached(false);
    } catch (e) {
      console.error("fetchProposals failed:", e);
      setProposals(MOCK_PROPOSALS);
      setUsingCached(true);
    } finally { setLoading(false); }
  }, [provider]);

  useEffect(() => { fetchProposals(); }, [fetchProposals]);

  async function handleCreate() {
    if (!signer) return;
    try {
      setStatus("Creating proposal...");
      const dao          = new ethers.Contract(DAO_ADDRESS, DAO_ABI, signer);
      const callDataHex  = form.callData.startsWith("0x") ? form.callData : "0x" + form.callData;
      await (await dao.createProposal(form.description, form.target, callDataHex)).wait();
      setStatus("Proposal created on-chain!"); setShowForm(false);
    } catch (e) { setStatus("Error: " + (e.reason || e.message)); }
  }

  async function handleVote(id, support) {
    if (!signer) return;
    try {
      setStatus("Voting...");
      const dao = new ethers.Contract(DAO_ADDRESS, DAO_ABI, signer);
      await (await dao.vote(id, support)).wait();
      setStatus("Vote cast!");
    } catch (e) { setStatus("Error: " + (e.reason || e.message)); }
  }

  return (
    <SectionCard>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold text-white">Governance</h2>
        <div className="flex items-center gap-2 flex-wrap">
          {liveCount !== null && (
            <span className="text-xs font-mono bg-gray-800 text-gray-400 px-2 py-1 rounded">
              {liveCount} on-chain proposal{liveCount !== 1 ? "s" : ""}
            </span>
          )}
          {usingCachedData && (
            <span className="text-xs font-mono bg-orange-900/40 text-warning border border-warning/30 px-2 py-1 rounded">
              ⚠ Cached data
            </span>
          )}
          <button
            className="border border-gray-700 text-gray-400 hover:text-white hover:border-gray-500 px-3 py-1 rounded text-xs font-mono transition-colors disabled:opacity-40"
            onClick={fetchProposals}
            disabled={loading || !provider}
          >
            {loading ? "Loading..." : "Refresh"}
          </button>
          {signer && (
            <button
              className="bg-accent hover:bg-orange-600 text-white px-3 py-1 rounded text-xs font-semibold transition-colors"
              onClick={() => setShowForm(!showForm)}
            >
              {showForm ? "Cancel" : "+ New Proposal"}
            </button>
          )}
        </div>
      </div>

      {/* New proposal form */}
      {showForm && (
        <div className="bg-dark border border-gray-800 rounded-lg p-4 mb-4 flex flex-col gap-3">
          <textarea
            className="bg-surface border border-gray-700 text-gray-200 px-3 py-2 rounded-lg text-sm focus:outline-none focus:border-accent resize-y min-h-[80px] w-full"
            placeholder="Proposal description (be concise and specific)"
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
          />
          <input
            className="bg-surface border border-gray-700 text-gray-200 px-3 py-2 rounded-lg text-sm focus:outline-none focus:border-accent"
            placeholder="Target contract address (0x...)"
            value={form.target}
            onChange={(e) => setForm({ ...form, target: e.target.value })}
          />
          <input
            className="bg-surface border border-gray-700 text-gray-200 px-3 py-2 rounded-lg text-sm focus:outline-none focus:border-accent"
            placeholder="Call data (0x for no-op)"
            value={form.callData}
            onChange={(e) => setForm({ ...form, callData: e.target.value })}
          />
          <button
            className="bg-accent hover:bg-orange-600 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors self-start"
            onClick={handleCreate}
          >
            Submit On-Chain
          </button>
        </div>
      )}

      {/* Proposal cards */}
      <div className="space-y-4">
        {proposals.map((p) => {
          const total   = p.forVotes + p.againstVotes;
          const forPct  = total > 0n ? Number((p.forVotes * 100n) / total) : 0;
          const isActive = !p.executed && !p.canceled && Number(p.votingDeadline) > Date.now() / 1000;

          return (
            <div
              key={p.id}
              className="relative bg-dark border border-gray-800 rounded-lg p-5"
            >
              {/* Status badge — absolute top-right */}
              <span className={`absolute top-5 right-5 px-2 py-1 rounded text-xs font-mono ${
                p.executed
                  ? "bg-green-950 text-success border border-success/30"
                  : isActive
                  ? "bg-blue-950 text-blue-400 border border-blue-500/30"
                  : "bg-gray-900 text-gray-500 border border-gray-700"
              }`}>
                {p.executed ? "Executed" : p.canceled ? "Canceled" : isActive ? timeLeft(p.votingDeadline) : "Closed"}
              </span>

              <div className="text-xs font-mono text-gray-600 mb-2">#{p.id + 1}</div>
              <p className="text-sm text-gray-300 leading-relaxed pr-24 mb-2">{p.description}</p>
              <div className="text-xs text-gray-600 mb-3">By {shortAddr(p.proposer)}</div>

              {/* Progress bar */}
              <div className="h-2 bg-gray-800 rounded-full overflow-hidden mt-4">
                <div
                  className="h-full bg-accent rounded-full transition-all duration-500"
                  style={{ width: forPct + "%" }}
                />
              </div>
              <div className="flex justify-between mt-1 text-xs font-mono">
                <span className="text-success">{fmt(p.forVotes)} YES ({forPct}%)</span>
                <span className="text-red-400">{fmt(p.againstVotes)} NO</span>
              </div>

              {isActive && signer && (
                <div className="flex gap-2 mt-3">
                  <button
                    className="bg-accent hover:bg-orange-600 text-white px-3 py-1 rounded text-xs font-semibold transition-colors"
                    onClick={() => handleVote(p.id, true)}
                  >
                    Vote YES
                  </button>
                  <button
                    className="border border-red-500/40 text-red-400 hover:bg-red-950 px-3 py-1 rounded text-xs font-semibold transition-colors"
                    onClick={() => handleVote(p.id, false)}
                  >
                    Vote NO
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>
      {status && <p className="mt-3 text-sm font-mono text-accent">{status}</p>}
    </SectionCard>
  );
}

// ── Buyback & Burn ────────────────────────────────────────────────────────────

function BuybackSection({ provider }) {
  const [data, setData] = useState({ burned: null, pending: null });

  useEffect(() => {
    if (!provider) return;
    const buyback = new ethers.Contract(BUYBACK_ADDRESS, BUYBACK_ABI, provider);
    Promise.all([buyback.totalAlphaBurned(), buyback.pendingBurn()])
      .then(([burned, pending]) => setData({ burned, pending }))
      .catch((e) => console.error("Buyback load:", e));
  }, [provider]);

  return (
    <SectionCard>
      <h2 className="text-lg font-bold text-white mb-2">Buyback &amp; Burn</h2>
      <p className="text-sm text-gray-500 mb-4">
        Trading profits are used to buy PALPHA on the open market and burn it, reducing total supply.
      </p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-5">
        <div className="bg-dark border border-accent/20 rounded-lg p-4">
          <div className="text-xs font-mono text-gray-500 uppercase tracking-wider mb-1">Total PALPHA Burned</div>
          <div className="text-xl font-mono font-semibold text-white">{fmt(data.burned)} PALPHA</div>
        </div>
        <div className="bg-dark border border-gray-800 rounded-lg p-4">
          <div className="text-xs font-mono text-gray-500 uppercase tracking-wider mb-1">Pending Burn Queue</div>
          <div className="text-xl font-mono font-semibold text-white">{fmt(data.pending)} PALPHA</div>
        </div>
      </div>
      <div className="space-y-2">
        {[
          ["Buyback Contract", BUYBACK_ADDRESS],
          ["DAO Contract",     DAO_ADDRESS],
        ].map(([label, addr]) => (
          <div key={label} className="flex items-center justify-between py-2.5 border-b border-gray-800/60 text-sm">
            <span className="text-gray-400">{label}</span>
            <a
              href={"https://testnet.chainlab.fun/address/" + addr}
              target="_blank"
              rel="noreferrer"
              className="font-mono text-xs text-accent hover:underline"
            >
              {shortAddr(addr)}
            </a>
          </div>
        ))}
      </div>
    </SectionCard>
  );
}

// ── Main Page ─────────────────────────────────────────────────────────────────

const SECTION_TABS = [
  { id: "staking",    label: "Staking"       },
  { id: "governance", label: "Governance"    },
  { id: "buyback",    label: "Buyback & Burn" },
];

export default function PALPHAHubPage() {
  const [activeSection, setActiveSection] = useState("staking");
  const [provider,      setProvider]      = useState(null);
  const [signer,        setSigner]        = useState(null);
  const [address,       setAddress]       = useState(null);
  const [walletStatus,  setWalletStatus]  = useState("disconnected");

  async function connectWallet() {
    if (!window.ethereum) { alert("No wallet detected. Install MetaMask."); return; }
    try {
      setWalletStatus("connecting");
      const p    = new ethers.BrowserProvider(window.ethereum);
      await p.send("eth_requestAccounts", []);
      const s    = await p.getSigner();
      const addr = await s.getAddress();
      setProvider(p); setSigner(s); setAddress(addr); setWalletStatus("connected");
    } catch (e) {
      setWalletStatus("disconnected");
      console.error("Wallet connect:", e);
    }
  }

  return (
    <div>
      {/* Page header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-white">PALPHA Hub</h1>
          <p className="text-gray-400 mt-1 text-sm">Stake, govern, and track buyback activity for the PolyAlpha Protocol.</p>
        </div>
        <div>
          {walletStatus === "connected" ? (
            <span className="flex items-center gap-2 bg-dark border border-gray-700 rounded-lg px-3 py-2 font-mono text-sm text-accent">
              <span className="w-2 h-2 rounded-full bg-success shadow-[0_0_5px_#00E676]" />
              {shortAddr(address)}
            </span>
          ) : (
            <button
              className="bg-accent hover:bg-orange-600 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors"
              onClick={connectWallet}
            >
              {walletStatus === "connecting" ? "Connecting..." : "Connect Wallet"}
            </button>
          )}
        </div>
      </div>

      {/* Pill sub-navigation */}
      <div className="flex gap-2 mb-6">
        {SECTION_TABS.map((t) => (
          <button
            key={t.id}
            onClick={() => setActiveSection(t.id)}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
              activeSection === t.id
                ? "bg-accent text-white"
                : "bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {activeSection === "staking"    && <StakingSection    provider={provider} signer={signer} address={address} />}
      {activeSection === "governance" && <GovernanceSection provider={provider} signer={signer} address={address} />}
      {activeSection === "buyback"    && <BuybackSection    provider={provider} />}
    </div>
  );
}
