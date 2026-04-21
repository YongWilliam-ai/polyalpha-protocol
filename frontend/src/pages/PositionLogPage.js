import React, { useState, useEffect } from "react";
import { ethers } from "ethers";
import { VAULT_ADDRESS, VAULT_ABI, POLYGONSCAN_URL, RPC_URL } from "../config";

const MAX_EVENTS = 50;

export default function PositionLogPage() {
  const [signals, setSignals]   = useState([]);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState(null);
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

      // Look back up to 10,000 blocks (~3 days on Polygon Amoy)
      const fromBlock = Math.max(0, current - 10_000);
      setLastBlock(current);

      const filter = vault.filters.PositionLogged();
      const events = await vault.queryFilter(filter, fromBlock, current);

      const parsed = events
        .slice(-MAX_EVENTS)
        .reverse()  // newest first
        .map((e) => ({
          txHash:        e.transactionHash,
          block:         e.blockNumber,
          timestamp:     new Date(Number(e.args.timestamp) * 1000).toISOString().replace("T", " ").slice(0, 19),
          market:        e.args.marketQuestion,
          aiProbPct:     (Number(e.args.aiProbabilityBps) / 100).toFixed(1),
          marketPricePct:(Number(e.args.marketPriceBps) / 100).toFixed(1),
          edgePct:       (Number(e.args.edgeBps) / 100).toFixed(1),
          side:          e.args.side,
          kellyPct:      (Number(e.args.kellyFractionBps) / 100).toFixed(2),
          oracleHash:    e.args.oracleInputHash,
        }));

      setSignals(parsed);
    } catch (e) {
      setError(`Failed to load on-chain events: ${e.message}`);
    }
    setLoading(false);
  };

  if (loading) return <div className="page"><p>Loading on-chain signal events...</p></div>;

  return (
    <div className="page">
      <div className="page-header">
        <h2>AI Signal Audit Log</h2>
        <button className="btn-outline btn-sm" onClick={loadSignals}>↻ Refresh</button>
      </div>

      <div className="notice info">
        <strong>On-chain audit trail.</strong> Every signal the AI agent generates is logged
        immutably via <code>PositionLogged</code> events on Polygon Amoy.
        The <code>oracleInputHash</code> is SHA-256(btcOpen + btcNow + polyOdds + timestamp) —
        proving the agent's inputs were not manipulated after the fact.
        {lastBlock && <span> · Block height: {lastBlock.toLocaleString()}</span>}
      </div>

      {error && <div className="notice error">{error}</div>}

      {signals.length === 0 && !error && (
        <div className="notice info">
          No signals logged yet. Run <code>python agent/agent.py</code> to generate signals.
        </div>
      )}

      {signals.length > 0 && (
        <div className="table-wrap">
          <table className="signal-table">
            <thead>
              <tr>
                <th>Time (UTC)</th>
                <th>Market</th>
                <th>Side</th>
                <th>AI Prob</th>
                <th>Market Price</th>
                <th>Edge</th>
                <th>Kelly Size</th>
                <th>Oracle Hash</th>
                <th>Tx</th>
              </tr>
            </thead>
            <tbody>
              {signals.map((s, i) => (
                <tr key={i}>
                  <td className="mono">{s.timestamp}</td>
                  <td className="market-q" title={s.market}>{s.market.slice(0, 40)}…</td>
                  <td>
                    <span className={`badge badge-${s.side.toLowerCase()}`}>{s.side}</span>
                  </td>
                  <td className="num">{s.aiProbPct}%</td>
                  <td className="num">{s.marketPricePct}%</td>
                  <td className={`num ${Number(s.edgePct) > 0 ? "positive" : "negative"}`}>
                    {Number(s.edgePct) > 0 ? "+" : ""}{s.edgePct}%
                  </td>
                  <td className="num">{s.kellyPct}%</td>
                  <td className="mono hash" title={s.oracleHash}>
                    {s.oracleHash.slice(0, 10)}…
                  </td>
                  <td>
                    <a
                      href={`${POLYGONSCAN_URL}/tx/${s.txHash}`}
                      target="_blank"
                      rel="noreferrer"
                      className="tx-link"
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

      <div className="section">
        <h3>How to read this table</h3>
        <ul className="explainer">
          <li><strong>AI Prob</strong>: Agent's estimated win probability (BTC momentum-derived)</li>
          <li><strong>Market Price</strong>: Polymarket's current YES price at signal time</li>
          <li><strong>Edge</strong>: AI Prob − Market Price. Must be ≥8% for a signal to fire.</li>
          <li><strong>Kelly Size</strong>: Quarter-Kelly position recommendation as % of TVL</li>
          <li><strong>Oracle Hash</strong>: SHA-256(btcOpen, btcNow, polyOdds, timestamp) — tamper evidence stored on-chain</li>
          <li><strong>Tx ↗</strong>: Links to the immutable on-chain event on Polygonscan</li>
        </ul>
      </div>
    </div>
  );
}
