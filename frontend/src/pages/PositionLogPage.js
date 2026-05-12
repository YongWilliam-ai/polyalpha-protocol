import React, { useState, useEffect } from "react";
import { ethers } from "ethers";
import { VAULT_ADDRESS, VAULT_ABI, POLYGONSCAN_URL, RPC_URL } from "../config";

const MAX_EVENTS = 50;

export default function PositionLogPage() {
  const [signals,   setSignals]   = useState([]);
  const [loading,   setLoading]   = useState(true);
  const [error,     setError]     = useState(null);
  const [lastBlock, setLastBlock] = useState(null);

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
        }));
      setSignals(parsed);
    } catch (e) {
      setError(`Failed to load on-chain events: ${e.message}`);
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
          className="border border-gray-700 text-gray-400 hover:text-white hover:border-gray-500 px-3 py-1.5 rounded-lg text-xs font-mono transition-colors"
          onClick={loadSignals}
        >
          ↻ Refresh
        </button>
      </div>

      {/* On-chain audit explanation */}
      <div className="bg-blue-900/10 border border-blue-900/30 text-blue-200 p-4 rounded-lg text-sm mb-4">
        <strong>On-chain audit trail.</strong> Every signal the AI agent generates is logged immutably
        via <code className="bg-blue-900/30 px-1 rounded">PositionLogged</code> events on ChainLab Testnet.
        The <code className="bg-blue-900/30 px-1 rounded">oracleInputHash</code> is SHA-256(btcOpen + btcNow + polyOdds + timestamp) —
        proving the agent's inputs were not manipulated after the fact.
        {lastBlock && (
          <span className="text-blue-300"> · Block height: {lastBlock.toLocaleString()}</span>
        )}
      </div>

      {error && (
        <div className="bg-red-950 border border-red-500/30 text-red-300 p-4 rounded-lg text-sm mb-4">
          {error}
        </div>
      )}

      {signals.length === 0 && !error && (
        <div className="bg-surface border border-gray-800 text-gray-500 p-4 rounded-lg text-sm mb-4 font-mono">
          No signals logged yet. Run <code>python agent/agent.py</code> to generate signals.
        </div>
      )}

      {signals.length > 0 && (
        <div className="overflow-x-auto rounded-lg border border-gray-800">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-900 border-b border-gray-800">
                {["Time (UTC)", "Market", "Side", "AI Prob", "Mkt Price", "Edge", "Kelly", "Oracle Hash", "Tx"].map((h) => (
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
                  <td className="px-3 py-2.5 font-mono text-sm text-gray-300 max-w-[200px] truncate" title={s.market}>
                    {s.market.slice(0, 38)}…
                  </td>
                  <td className="px-3 py-2.5">
                    <span className={`px-2 py-0.5 rounded text-xs font-mono font-bold ${
                      s.side.toLowerCase() === "up"
                        ? "bg-green-950 text-success"
                        : "bg-red-950 text-red-400"
                    }`}>
                      {s.side}
                    </span>
                  </td>
                  <td className="px-3 py-2.5 font-mono text-sm text-white text-right">{s.aiProbPct}%</td>
                  <td className="px-3 py-2.5 font-mono text-sm text-gray-300 text-right">{s.marketPricePct}%</td>
                  <td className={`px-3 py-2.5 font-mono text-sm text-right ${
                    Number(s.edgePct) >= 8 ? "text-success" : Number(s.edgePct) > 0 ? "text-gray-300" : "text-red-400"
                  }`}>
                    {Number(s.edgePct) > 0 ? "+" : ""}{s.edgePct}%
                  </td>
                  <td className="px-3 py-2.5 font-mono text-sm text-gray-300 text-right">{s.kellyPct}%</td>
                  <td className="px-3 py-2.5 font-mono text-xs text-accent" title={s.oracleHash}>
                    {s.oracleHash.slice(0, 10)}…
                  </td>
                  <td className="px-3 py-2.5">
                    <a
                      href={`${POLYGONSCAN_URL}/tx/${s.txHash}`}
                      target="_blank"
                      rel="noreferrer"
                      className="text-accent hover:text-orange-400 transition-colors"
                    >
                      ↗
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Legend */}
      <div className="mt-6">
        <h3 className="text-xs font-mono text-gray-500 uppercase tracking-wider mb-3">How to read this table</h3>
        <ul className="space-y-1.5 text-sm text-gray-400">
          <li><span className="font-mono text-white">AI Prob</span>: Agent's estimated win probability (BTC momentum-derived)</li>
          <li><span className="font-mono text-white">Mkt Price</span>: Polymarket's current YES price at signal time</li>
          <li><span className="font-mono text-white">Edge</span>: AI Prob − Market Price. Must be ≥8% for a signal to fire.</li>
          <li><span className="font-mono text-white">Kelly</span>: Quarter-Kelly position recommendation as % of TVL</li>
          <li><span className="font-mono text-white">Oracle Hash</span>: SHA-256(btcOpen, btcNow, polyOdds, timestamp) — tamper evidence on-chain</li>
          <li><span className="font-mono text-white">Tx ↗</span>: Links to the immutable on-chain event on ChainLab Testnet Explorer</li>
        </ul>
      </div>
    </div>
  );
}
