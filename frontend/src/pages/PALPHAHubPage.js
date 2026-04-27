import React, { useState, useEffect, useCallback } from "react";
import { ethers } from "ethers";
import {
  STAKING_ADDRESS, STAKING_ABI,
  BUYBACK_ADDRESS, BUYBACK_ABI,
  PALPHA_ADDRESS, PALPHA_ABI,
  DAO_ADDRESS, DAO_ABI,
} from "../config";

// ── Helpers ───────────────────────────────────────────────────────────────────

function fmt(wei, decimals = 18) {
  if (wei === null || wei === undefined) return "—";
  try {
    return parseFloat(ethers.formatUnits(wei, decimals)).toLocaleString(undefined, {
      maximumFractionDigits: 2,
    });
  } catch {
    return "—";
  }
}

function shortAddr(addr) {
  if (!addr) return "—";
  return addr.slice(0, 6) + "..." + addr.slice(-4);
}

function timeLeft(deadline) {
  const now = Math.floor(Date.now() / 1000);
  const diff = Number(deadline) - now;
  if (diff <= 0) return "Closed";
  const h = Math.floor(diff / 3600);
  const m = Math.floor((diff % 3600) / 60);
  return h + "h " + m + "m left";
}

// ── Section: Staking ──────────────────────────────────────────────────────────

function StakingSection({ provider, signer, address }) {
  const [data, setData] = useState({ staked: null, earned: null, total: null });
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
    } catch (e) {
      console.error("Staking load:", e);
    }
  }, [provider, address]);

  useEffect(() => { load(); }, [load]);

  async function approve(amountWei) {
    const palpha = new ethers.Contract(PALPHA_ADDRESS, PALPHA_ABI, signer);
    const tx = await palpha.approve(STAKING_ADDRESS, amountWei);
    await tx.wait();
  }

  async function handleStake() {
    try {
      setStatus("Approving...");
      const amountWei = ethers.parseEther(amount);
      await approve(amountWei);
      setStatus("Staking...");
      const staking = new ethers.Contract(STAKING_ADDRESS, STAKING_ABI, signer);
      const tx = await staking.stake(amountWei);
      await tx.wait();
      setStatus("Staked!");
      setAmount("");
      load();
    } catch (e) {
      setStatus("Error: " + (e.reason || e.message));
    }
  }

  async function handleUnstake() {
    try {
      setStatus("Unstaking...");
      const amountWei = ethers.parseEther(amount);
      const staking = new ethers.Contract(STAKING_ADDRESS, STAKING_ABI, signer);
      const tx = await staking.unstake(amountWei);
      await tx.wait();
      setStatus("Unstaked!");
      setAmount("");
      load();
    } catch (e) {
      setStatus("Error: " + (e.reason || e.message));
    }
  }

  async function handleClaim() {
    try {
      setStatus("Claiming...");
      const staking = new ethers.Contract(STAKING_ADDRESS, STAKING_ABI, signer);
      const tx = await staking.claimReward();
      await tx.wait();
      setStatus("Claimed!");
      load();
    } catch (e) {
      setStatus("Error: " + (e.reason || e.message));
    }
  }

  return (
    <div className="hub-section">
      <h2 className="hub-section-title">PALPHA Staking</h2>
      <div className="hub-stats-grid">
        <div className="hub-stat">
          <span className="hub-stat-label">Your Staked</span>
          <span className="hub-stat-value">{fmt(data.staked)} PALPHA</span>
        </div>
        <div className="hub-stat">
          <span className="hub-stat-label">Earned Rewards</span>
          <span className="hub-stat-value">{fmt(data.earned)} PALPHA</span>
        </div>
        <div className="hub-stat">
          <span className="hub-stat-label">Total Pool Staked</span>
          <span className="hub-stat-value">{fmt(data.total)} PALPHA</span>
        </div>
      </div>
      {signer ? (
        <div className="hub-actions">
          <input
            className="hub-input"
            type="number"
            placeholder="Amount (PALPHA)"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
          />
          <button className="hub-btn primary" onClick={handleStake}>Stake</button>
          <button className="hub-btn" onClick={handleUnstake}>Unstake</button>
          <button className="hub-btn accent" onClick={handleClaim}>Claim Rewards</button>
        </div>
      ) : (
        <p className="hub-connect-note">Connect wallet to stake</p>
      )}
      {status && <p className="hub-status">{status}</p>}
    </div>
  );
}

// ── Section: Governance ───────────────────────────────────────────────────────

const MOCK_PROPOSALS = [
  {
    id: 0,
    proposer: "0xfEe9eeC07f9f689aA2F81e240f3199E02f93896d",
    description: "Increase vault max drawdown circuit breaker from 20% to 25% to allow longer trend trades.",
    forVotes: ethers.parseEther("320000"),
    againstVotes: ethers.parseEther("80000"),
    executed: true,
    canceled: false,
    votingDeadline: BigInt(Math.floor(Date.now() / 1000) - 86400),
  },
  {
    id: 1,
    proposer: "0xfEe9eeC07f9f689aA2F81e240f3199E02f93896d",
    description: "Allocate 5% of buyback revenue to a community grants multisig for ecosystem development.",
    forVotes: ethers.parseEther("150000"),
    againstVotes: ethers.parseEther("20000"),
    executed: false,
    canceled: false,
    votingDeadline: BigInt(Math.floor(Date.now() / 1000) + 3600 * 36),
  },
];

function GovernanceSection({ provider, signer, address }) {
  const [proposals, setProposals] = useState(MOCK_PROPOSALS);
  const [liveCount, setLiveCount] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ description: "", target: "", callData: "0x" });
  const [status, setStatus] = useState("");

  useEffect(() => {
    if (!provider) return;
    const dao = new ethers.Contract(DAO_ADDRESS, DAO_ABI, provider);
    dao.proposalCount().then((n) => setLiveCount(Number(n))).catch(() => {});
  }, [provider]);

  async function handleCreate() {
    if (!signer) return;
    try {
      setStatus("Creating proposal...");
      const dao = new ethers.Contract(DAO_ADDRESS, DAO_ABI, signer);
      const callDataHex = form.callData.startsWith("0x") ? form.callData : "0x" + form.callData;
      const tx = await dao.createProposal(form.description, form.target, callDataHex);
      await tx.wait();
      setStatus("Proposal created on-chain!");
      setShowForm(false);
    } catch (e) {
      setStatus("Error: " + (e.reason || e.message));
    }
  }

  async function handleVote(id, support) {
    if (!signer) return;
    try {
      setStatus("Voting...");
      const dao = new ethers.Contract(DAO_ADDRESS, DAO_ABI, signer);
      const tx = await dao.vote(id, support);
      await tx.wait();
      setStatus("Vote cast!");
    } catch (e) {
      setStatus("Error: " + (e.reason || e.message));
    }
  }

  return (
    <div className="hub-section">
      <div className="hub-section-header">
        <h2 className="hub-section-title">Governance</h2>
        <div className="hub-section-meta">
          {liveCount !== null && (
            <span className="hub-badge">{liveCount} on-chain proposal{liveCount !== 1 ? "s" : ""}</span>
          )}
          {signer && (
            <button className="hub-btn primary" onClick={() => setShowForm(!showForm)}>
              {showForm ? "Cancel" : "+ New Proposal"}
            </button>
          )}
        </div>
      </div>

      {showForm && (
        <div className="hub-form">
          <textarea
            className="hub-input hub-textarea"
            placeholder="Proposal description (be concise and specific)"
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
          />
          <input
            className="hub-input"
            placeholder="Target contract address (0x...)"
            value={form.target}
            onChange={(e) => setForm({ ...form, target: e.target.value })}
          />
          <input
            className="hub-input"
            placeholder="Call data (0x for no-op)"
            value={form.callData}
            onChange={(e) => setForm({ ...form, callData: e.target.value })}
          />
          <button className="hub-btn primary" onClick={handleCreate}>Submit On-Chain</button>
        </div>
      )}

      <div className="hub-proposals">
        {proposals.map((p) => {
          const total = p.forVotes + p.againstVotes;
          const forPct = total > 0n ? Number((p.forVotes * 100n) / total) : 0;
          const isActive = !p.executed && !p.canceled && Number(p.votingDeadline) > Date.now() / 1000;
          return (
            <div key={p.id} className={`hub-proposal ${p.executed ? "executed" : isActive ? "active" : "expired"}`}>
              <div className="hub-proposal-header">
                <span className="hub-proposal-id">#{p.id + 1}</span>
                <span className={`hub-proposal-status ${p.executed ? "executed" : isActive ? "active" : "expired"}`}>
                  {p.executed ? "Executed" : p.canceled ? "Canceled" : isActive ? timeLeft(p.votingDeadline) : "Closed"}
                </span>
              </div>
              <p className="hub-proposal-desc">{p.description}</p>
              <div className="hub-proposal-meta">
                <span>By {shortAddr(p.proposer)}</span>
              </div>
              <div className="hub-vote-bar-wrap">
                <div className="hub-vote-bar">
                  <div className="hub-vote-for" style={{ width: forPct + "%" }} />
                </div>
                <div className="hub-vote-labels">
                  <span className="for">{fmt(p.forVotes)} YES ({forPct}%)</span>
                  <span className="against">{fmt(p.againstVotes)} NO</span>
                </div>
              </div>
              {isActive && signer && (
                <div className="hub-vote-actions">
                  <button className="hub-btn primary small" onClick={() => handleVote(p.id, true)}>Vote YES</button>
                  <button className="hub-btn danger small" onClick={() => handleVote(p.id, false)}>Vote NO</button>
                </div>
              )}
            </div>
          );
        })}
      </div>
      {status && <p className="hub-status">{status}</p>}
    </div>
  );
}

// ── Section: Buyback & Burn ───────────────────────────────────────────────────

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
    <div className="hub-section">
      <h2 className="hub-section-title">Buyback & Burn</h2>
      <p className="hub-section-subtitle">
        Trading profits are used to buy PALPHA on the open market and burn it, reducing total supply.
      </p>
      <div className="hub-stats-grid">
        <div className="hub-stat accent">
          <span className="hub-stat-label">Total PALPHA Burned</span>
          <span className="hub-stat-value">{fmt(data.burned)} PALPHA</span>
        </div>
        <div className="hub-stat">
          <span className="hub-stat-label">Pending Burn Queue</span>
          <span className="hub-stat-value">{fmt(data.pending)} PALPHA</span>
        </div>
      </div>
      <div className="hub-burn-info">
        <div className="hub-burn-row">
          <span>Buyback Contract</span>
          <a
            href={"https://testnet.chainlab.fun/address/" + BUYBACK_ADDRESS}
            target="_blank"
            rel="noreferrer"
            className="hub-link"
          >
            {shortAddr(BUYBACK_ADDRESS)}
          </a>
        </div>
        <div className="hub-burn-row">
          <span>DAO Contract</span>
          <a
            href={"https://testnet.chainlab.fun/address/" + DAO_ADDRESS}
            target="_blank"
            rel="noreferrer"
            className="hub-link"
          >
            {shortAddr(DAO_ADDRESS)}
          </a>
        </div>
      </div>
    </div>
  );
}

// ── Main Page ─────────────────────────────────────────────────────────────────

const SECTION_TABS = [
  { id: "staking",   label: "Staking" },
  { id: "governance", label: "Governance" },
  { id: "buyback",   label: "Buyback & Burn" },
];

export default function PALPHAHubPage() {
  const [activeSection, setActiveSection] = useState("staking");
  const [provider, setProvider] = useState(null);
  const [signer, setSigner] = useState(null);
  const [address, setAddress] = useState(null);
  const [walletStatus, setWalletStatus] = useState("disconnected");

  async function connectWallet() {
    if (!window.ethereum) {
      alert("No wallet detected. Install MetaMask to interact with contracts.");
      return;
    }
    try {
      setWalletStatus("connecting");
      const p = new ethers.BrowserProvider(window.ethereum);
      await p.send("eth_requestAccounts", []);
      const s = await p.getSigner();
      const addr = await s.getAddress();
      setProvider(p);
      setSigner(s);
      setAddress(addr);
      setWalletStatus("connected");
    } catch (e) {
      setWalletStatus("disconnected");
      console.error("Wallet connect:", e);
    }
  }

  return (
    <div className="hub-page">
      <div className="hub-header">
        <div>
          <h1 className="hub-title">PALPHA Hub</h1>
          <p className="hub-subtitle">Stake, govern, and track buyback activity for the PolyAlpha Protocol.</p>
        </div>
        <div className="hub-wallet">
          {walletStatus === "connected" ? (
            <span className="hub-wallet-addr">{shortAddr(address)}</span>
          ) : (
            <button className="hub-btn primary" onClick={connectWallet}>
              {walletStatus === "connecting" ? "Connecting..." : "Connect Wallet"}
            </button>
          )}
        </div>
      </div>

      <div className="hub-section-tabs">
        {SECTION_TABS.map((t) => (
          <button
            key={t.id}
            className={`hub-section-tab ${activeSection === t.id ? "active" : ""}`}
            onClick={() => setActiveSection(t.id)}
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
