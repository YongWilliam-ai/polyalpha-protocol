import React, { useState, useEffect } from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine,
} from "recharts";
import { DataCard } from "../components/DataCard";

export default function BacktestPage() {
  const [summary,     setSummary]  = useState(null);
  const [equityCurve, setEquity]   = useState([]);
  const [loading,     setLoading]  = useState(true);
  const [error,       setError]    = useState(null);

  useEffect(() => {
    Promise.all([
      fetch("/backtest_summary.json").then((r) => r.json()).catch(() => null),
      fetch("/equity_curve.csv").then((r) => r.text()).catch(() => null),
    ]).then(([sum, csv]) => {
      setSummary(sum);
      if (csv) {
        const lines = csv.trim().split("\n").slice(1);
        setEquity(lines.map((line) => {
          const [trade, cumPnl, equity] = line.split(",");
          return { trade: parseInt(trade), cumPnlPct: parseFloat(cumPnl), equityIdx: parseFloat(equity) };
        }));
      }
      setLoading(false);
    }).catch((e) => { setError(e.message); setLoading(false); });
  }, []);

  if (loading) return (
    <div className="text-gray-500 font-mono text-sm p-6 animate-pulse">Loading backtest results...</div>
  );

  const hasData = summary && !summary.error;

  return (
    <div>
      <h2 className="text-2xl font-bold text-white mb-4">Backtest Results — BTC 7-Minute Momentum Signal</h2>

      <div className="bg-surface border border-gray-800 text-gray-300 p-4 rounded-lg text-sm mb-4">
        <strong className="text-white">Methodology:</strong> Tests the 7-minute BTC momentum hypothesis on closed
        Polymarket markets. At T+7 min, if BTC moved &gt;0.3% AND Polymarket odds were &lt;62% for that direction,
        the strategy would have entered. Results use Quarter-Kelly sizing and assume paper trading (no slippage modeled in v1).
        <br /><br />
        <span className="text-warning font-medium">Important limitation:</span> This backtest approximates T+7 signals from
        market metadata. Tick-level backtesting with real order book data is a Phase 2 improvement.
        Treat results as directional, not definitive.
      </div>

      {error && (
        <div className="bg-red-950 border border-red-500/30 text-red-300 p-4 rounded-lg text-sm mb-4">
          Failed to load data: {error}<br />
          Run <code className="bg-gray-900 px-1 rounded">python agent/backtest.py</code> then copy results to{" "}
          <code className="bg-gray-900 px-1 rounded">frontend/public/</code>
        </div>
      )}

      {!hasData && !error && (
        <div className="bg-yellow-950/30 border border-yellow-700/30 text-yellow-200 p-4 rounded-lg text-sm mb-4">
          No backtest data found. Run:{" "}
          <code className="bg-gray-900 px-1 rounded">cd agent &amp;&amp; python backtest.py</code>
        </div>
      )}

      {hasData && (
        <>
          {/* DataCards — Prompt 4 Task 2 */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-6">
            <DataCard label="Total Trades"  value={summary.n_trades} />
            <DataCard
              label="Win Rate"
              value={<span className="text-success">{summary.win_rate_pct}%</span>}
              alert={summary.win_rate_pct < 55}
            />
            <DataCard label="Avg Edge"     value={`${summary.avg_edge_pct}%`} />
            <DataCard label="Sharpe Ratio" value={summary.sharpe_ratio}       alert={summary.sharpe_ratio < 0.8} />
            <DataCard label="Max Drawdown" value={`${summary.max_drawdown_pct}%`} alert={summary.max_drawdown_pct < -20} />
            <DataCard label="Total P&L"    value={`${summary.total_pnl_pct > 0 ? "+" : ""}${summary.total_pnl_pct}%`} />
          </div>

          {/* Hypothesis verdict */}
          {summary.win_rate_pct >= 58 && (
            <div className="bg-success/10 border border-success/30 text-success p-4 rounded-lg font-mono text-sm mb-4">
              ✓ Win rate ≥58%: Hypothesis SUPPORTED — the 7-minute BTC momentum signal has measurable edge on historical data.
            </div>
          )}
          {summary.win_rate_pct >= 52 && summary.win_rate_pct < 58 && (
            <div className="bg-yellow-950/30 border border-yellow-700/30 text-yellow-200 p-4 rounded-lg font-mono text-sm mb-4">
              △ Win rate 52–58%: Weak positive edge. More data or refined entry rules needed before live deployment.
            </div>
          )}
          {summary.win_rate_pct < 52 && (
            <div className="bg-red-950 border border-red-500/30 text-red-300 p-4 rounded-lg font-mono text-sm mb-4">
              ✗ Win rate &lt;52%: Hypothesis NOT supported. Signal rules need revision before live deployment.
            </div>
          )}

          {/* Equity curve */}
          {equityCurve.length > 0 && (
            <div className="bg-surface border border-gray-800 rounded-lg p-4 mb-6">
              <h3 className="text-xs font-mono text-gray-500 uppercase tracking-wider mb-4">Equity Curve (indexed to 100)</h3>
              <ResponsiveContainer width="100%" height={320}>
                <LineChart data={equityCurve} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1E1B29" />
                  <XAxis
                    dataKey="trade"
                    label={{ value: "Trade #", position: "insideBottom", offset: -3, fill: "#6b7280" }}
                    tick={{ fill: "#6b7280", fontSize: 11 }}
                  />
                  <YAxis tick={{ fill: "#6b7280", fontSize: 11 }} />
                  <Tooltip
                    contentStyle={{ background: "#16141E", border: "1px solid #374151", color: "#e5e7eb" }}
                    formatter={(v, name) => [v.toFixed(2), name === "equityIdx" ? "Equity Index" : "Cumulative P&L %"]}
                  />
                  <ReferenceLine y={100} stroke="#374151" strokeDasharray="4 4" />
                  <Line type="monotone" dataKey="equityIdx" stroke="#FF4500" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
              <p className="text-xs text-gray-600 font-mono mt-2">
                Starting index = 100. Each trade uses Quarter-Kelly sizing (max 5% TVL).
              </p>
            </div>
          )}

          {/* Assumptions table */}
          <div>
            <h3 className="text-xs font-mono text-gray-500 uppercase tracking-wider mb-3">Explicit Assumptions (A1–A6)</h3>
            <div className="bg-surface border border-gray-800 rounded-lg overflow-hidden">
              <table className="w-full text-sm">
                <tbody>
                  {[
                    ["A1", "Favorite-longshot bias persists in BTC 15m markets",        "To be validated by this backtest"],
                    ["A2", "BTC 7-min momentum >0.3% provides ≥8% edge",               "HYPOTHESIS — validated by result above"],
                    ["A3", "Quarter-Kelly (25% of full Kelly) used for safety",         "Standard institutional practice (Kelly 1956)"],
                    ["A4", "All v1 trading is testnet only; no real funds",             "Explicit prototype scope"],
                    ["A5", "Tick-level T+7 data not available; metadata used as proxy","Phase 2: marketlens-python L2 data"],
                    ["A6", "No slippage modeled in v1 backtest",                        "Conservative real edge = backtest edge − est. 1–2% slippage"],
                  ].map(([id, assumption, note]) => (
                    <tr key={id} className="border-b border-gray-800 last:border-0">
                      <td className="px-4 py-3 font-mono text-gray-500 text-xs w-10">{id}</td>
                      <td className="px-4 py-3 text-gray-300">{assumption}</td>
                      <td className="px-4 py-3 text-gray-500 text-xs">{note}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
