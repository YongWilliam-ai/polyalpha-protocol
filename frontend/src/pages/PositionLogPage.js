import React, { useState, useEffect } from "react";
import { ethers } from "ethers";
import { VAULT_ADDRESS, VAULT_ABI, POLYGONSCAN_URL, RPC_URL } from "../config";

const MAX_EVENTS = 50;

// Demo signals for presentation when no on-chain events exist yet
const DEMO_SIGNALS = [
  {
    timestamp: "2026-05-12 14:32:07",
    market: "Will BTC close above $105,000 on any day before July 2026?",
    side: "BUY",
    aiProbPct: "74.2",
    marketPricePct: "61.0",
    edgePct: "13.2",
    kellyPct: "3.30",
    oracleHash: "0x8a3f2b1c9d...tamper-proof",
    txHash: null,
    block: 12847291,
    isDemo: true,
  },
  {
    timestamp: "2026-05-12 11:15:43",
    market: "Will ETH reach $4,000 before August 2026?",
    side: "BUY",
    aiProbPct: "68.5",
    marketPricePct: "55.3",
    edgePct: "13.2",
    kellyPct: "3.30",
    oracleHash: "0x7c4e9a2f1b...tamper-proof",
    txHash: null,
    block: 12847185,
    isDemo: true,
  },
  {
    timestamp: "2026-05-11 22:08:19",
    market: "Will the Fed cut rates in June 2026?",
    side: "SKIP",
    aiProbPct: "52.1",
    marketPricePct: "49.8",
    edgePct: "2.3",
    kellyPct: "0.00",
    oracleHash: "0x3d1f8e7a5c...tamper-proof",
    txHash: null,
    block: 12846992,
    isDemo: true,
  },
  {
    timestamp: "2026-05-11 16:44:55",
    market: "Will BTC close above $100,000 on any day before June 2026?",
    side: "BUY",
    aiProbPct: "81.3",
    marketPricePct: "72.0",
    edgePct: "9.3",
    kellyPct: "2.33",
    oracleHash: "0x5b2c4d9e8f...tamper-proof",
    txHash: null,
    block: 12846801,
    isDemo: true,
  },
  {
    timestamp: "2026-05-11 09:22:31",
    market: "Will SOL reach $200 before September 2026?",
    side: "SELL",
    aiProbPct: "31.2",
    marketPricePct: "44.5",
    edgePct: "13.3",
    kellyPct: "3.33",
    oracleHash: "0x9f1a3c7b2d...tamper-proof",
    txHash: null,
    block: 12846655,
    isDemo: true,
  },
  {
    timestamp: "2026-05-10 20:55:12",
    market: "Will Trump win the 2028 Republican primary?",
    side: "SKIP",
    aiProbPct: "45.8",
    marketPricePct: "48.2",
    edgePct: "-2.4",
    kellyPct: "0.00",
    oracleHash: "0x2e8d5f4a1c...tamper-proof",
    txHash: null,
    block: 12846412,
    isDemo: true,
  },
];

export default function PositionLogPage() {
  const [signals,   setSignals]   = useState([]);
  const [loading,   setLoading]   = useState(true);
  const [error,     setError]     = useState(null);
  const [lastBlock, setLastBlock] = useState(null);
  const [usingDemo, setUsingDemo] = useState(false);

  useEffect(() => {
    if (!VAULT_ADDRESS) {
      setLoading(false);
      setError("Vault not deployed — deploy first and set REACT_APP_VAULT_ADDRESS");
      return;
    }
    loadSignals();
  }, []);

  const loadSignals = async () => {
    setLoading(true);
    try {
      const provider = new ethers.JsonRpcProvider(RPC_URL);
      const vault    = new ethers.Contract(VAULT_ADDRESS, VAULT_ABI, provider);
      const current  = await provider.getBlockNumber();
      const fromBlock = Math.max(0, current - 10_000);
      setLastBlock(current);

      const events = await vault.queryFilter(vault.filters.PositionLogged(), fromBlock, current);
      const parsed = events
        .slice(-MAX_EVENTS)
        .reverse()
        .map((e) => ({
          txHash:         e.transactionHash,
          block:          e.blockNumber,
          timestamp:      new Date(Number(e.args.timestamp) * 1000).toISOString().replace("T", " ").slice(0, 19),
          market:         e.args.marketQuestion,
          aiProbPct:      (Number(e.args.aiProbabilityBps) / 100).toFixed(1),
          marketPricePct: (Number(e.args.marketPriceBps) / 100).toFixed(1),
          edgePct:        (Number(e.args.edgeBps) / 100).toFixed(1),
          side:           e.args.side,
          kellyPct:       (Number(e.args.kellyFractionBps) / 100).toFixed(2),
          oracleHash:     e.args.oracleInputHash,
          isDemo:         false,
        }));

      if (parsed.length > 0) {
        setSignals(parsed);
        setUsingDemo(false);
      } else {
        setSignals(DEMO_SIGNALS);
        setUsingDemo(true);
      }
    } catch (e) {
      // Fallback to demo signals on RPC error
      setSignals(DEMO_SIGNALS);
      setUsingDemo(true);
    }
    setLoading(false);
  };

  if (loading) return (
    <div className="text-gray-500 font-mono text-sm p-6 animate-pulse">
      Loading on-chain signal events...
    </div>
  );

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-white">AI Signal Audit Log</h2>
        <button
          className="border border-gray-700 text-gray-400 hover:text-white hover:border-gray-500 px-3 py-1.5 text-xs font-mono transition-colors"
          onClick={loadSignals}
        >
          ↻ Refresh
        </button>
      </div>

      {/* On-chain audit explanation */}
      <div className="bg-surface border border-accent/20 text-gray-300 p-4 text-sm mb-4">
        <strong className="text-accent">On-chain audit trail.</strong> Every signal the AI agent generates is logged immutably
        via <code className="bg-gray-800 px-1 text-accent">PositionLogged</code> events on ChainLab Testnet.
        The <code className="bg-gray-800 px-1 text-accent">oracleInputHash</code> is SHA-256(btcOpen + btcNow + polyOdds + timestamp) —
        proving the agent's inputs were not manipulated after the fact.
        {lastBlock && (
          <span className="text-gray-500 ml-2">· Block height: {lastBlock.toLocaleString()}</span>
        )}
      </div>

      {usingDemo && (
        <div className="bg-dark border border-yellow-700/30 text-yellow-400 p-3 font-mono text-xs mb-4">
          <span className="font-bold">DEMO MODE</span> — Showing simulated signals for presentation.
          In production, these are fetched from on-chain PositionLogged events.
        </div>
      )}

      {error && (
        <div className="bg-dark border border-red-500/30 text-red-300 p-4 text-sm mb-4 font-mono">
          {error}
        </div>
      )}

      {signals.length > 0 && (
        <div className="overflow-x-auto border border-gray-800">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-900 border-b border-gray-800">
                {["Time (UTC)", "Market", "Side", "AI Prob", "Mkt Price", "Edge", "Kelly", "Oracle Hash"].map((h) => (
                  <th key={h} className="px-3 py-2.5 text-left text-xs font-mono text-gray-500 uppercase tracking-wider whitespace-nowrap">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {signals.map((s, i) => (
                <tr key={i} className="hover:bg-surface-hover border-b border-gray-800/50 transition-colors">
                  <td className="px-3 py-2.5 font-mono text-sm text-gray-400 whitespace-nowrap">{s.timestamp}</td>
                  <td className="px-3 py-2.5 font-mono text-sm text-gray-300 max-w-[220px] truncate" title={s.market}>
                    {s.market.length > 42 ? s.market.slice(0, 42) + "…" : s.market}
                  </td>
                  <td className="px-3 py-2.5">
                    <span className={`px-2 py-0.5 text-xs font-mono font-bold ${
                      s.side === "BUY"
                        ? "bg-green-950 text-success"
                        : s.side === "SELL"
                        ? "bg-red-950 text-red-400"
                        : "bg-gray-800 text-gray-500"
                    }`}>
                      {s.side}
                    </span>
                  </td>
                  <td className="px-3 py-2.5 font-mono text-sm text-white text-right">{s.aiProbPct}%</td>
                  <td className="px-3 py-2.5 font-mono text-sm text-gray-300 text-right">{s.marketPricePct}%</td>
                  <td className={`px-3 py-2.5 font-mono text-sm text-right ${
                    Number(s.edgePct) >= 8 ? "text-success" : Number(s.edgePct) >= 3 ? "text-yellow-400" : "text-gray-500"
                  }`}>
                    {Number(s.edgePct) > 0 ? "+" : ""}{s.edgePct}%
                  </td>
                  <td className="px-3 py-2.5 font-mono text-sm text-gray-300 text-right">{s.kellyPct}%</td>
                  <td className="px-3 py-2.5 font-mono text-xs text-accent">
                    {s.oracleHash.slice(0, 14)}…
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Legend */}
      <div className="mt-6">
        <div className="text-xs font-mono text-gray-500 uppercase tracking-wider mb-3">// signal_interpretation</div>
        <div className="bg-surface border border-gray-800 p-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm text-gray-400">
            <div><span className="font-mono text-white">AI Prob</span>: Agent's estimated win probability (momentum + swarm consensus)</div>
            <div><span className="font-mono text-white">Mkt Price</span>: Polymarket's current YES price at signal time</div>
            <div><span className="font-mono text-white">Edge</span>: AI Prob − Market Price. Must be ≥3% (300 bps) for execution.</div>
            <div><span className="font-mono text-white">Kelly</span>: Quarter-Kelly position size as % of TVL (max 5%)</div>
            <div><span className="font-mono text-white">Oracle Hash</span>: SHA-256 proof of inputs — tamper evidence on-chain</div>
            <div><span className="font-mono text-white">SKIP</span>: Edge below threshold — agent observed but did not trade</div>
          </div>
        </div>
      </div>
    </div>
  );
}
