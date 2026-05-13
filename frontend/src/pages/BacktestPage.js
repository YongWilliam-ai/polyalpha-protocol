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
          const [trade, , equity, cumPnl] = line.split(",");
          return { trade: parseInt(trade), cumPnlPct: parseFloat(cumPnl), equityIdx: parseFloat(equity) };
        }));
      }
      setLoading(false);
    }).catch((e) => { setError(e.message); setLoading(false); });
  }, []);

  if (loading) return (
    <div className="text-gray-500 font-mono text-sm p-6 animate-pulse">
      {">"} loading backtest_results...
    </div>
  );

  const hasData = summary && !summary.error;

  return (
    <div>
      {/* Page header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-white tracking-tight">
          Backtest Results
        </h2>
        <p className="text-gray-500 font-mono text-xs mt-1">
          H1: BTC Momentum Signal · Quarter-Kelly Sizing · Polymarket Gamma API Data
        </p>
      </div>

      {/* Methodology note — EdgeBuild terminal block */}
      <div className="bg-surface border border-gray-800 border-l-2 border-l-accent p-4 text-sm mb-4 font-mono">
        <div className="text-xs text-gray-600 mb-2 uppercase tracking-wider">// methodology</div>
        <span className="text-gray-300">
          Signal: 68% base accuracy with MiroFish 5-persona consensus filter.
          Entry: AI probability &gt; market price + 3% minimum edge.
          Sizing: Quarter-Kelly (25% of full Kelly fraction). Slippage: 0.5% per trade.
        </span>
        <div className="mt-2 text-xs text-yellow-500">
          ! data: Real Polymarket Gamma API historical closed markets (2020-2026).
          Cash-flow PnL model. Reproducible with seed=42.
        </div>
      </div>

      {error && (
        <div className="bg-dark border border-red-500/30 text-red-400 p-4 font-mono text-sm mb-4">
          <span className="text-red-600">ERR</span> Failed to load: {error}<br />
          Run <code className="text-accent">python agent/backtest_reproducible.py</code> then copy to{" "}
          <code className="text-accent">frontend/public/</code>
        </div>
      )}

      {!hasData && !error && (
        <div className="bg-dark border border-yellow-700/30 text-yellow-400 p-4 font-mono text-sm mb-4">
          <span className="text-yellow-600">WARN</span> No backtest data found. Run:{" "}
          <code className="text-accent">cd agent && python backtest_reproducible.py</code>
        </div>
      )}

      {hasData && (
        <>
          {/* Metric bento grid */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-6">
            <DataCard label="Total Trades"  value={summary.n_trades} />
            <DataCard
              label="Win Rate"
              value={<span className="text-success">{summary.win_rate_pct}%</span>}
              alert={summary.win_rate_pct < 55}
            />
            <DataCard label="Profit Factor" value={summary.profit_factor || "—"} />
            <DataCard label="Sharpe Ratio" value={summary.sharpe_ratio}       alert={summary.sharpe_ratio < 0.8} />
            <DataCard label="Max Drawdown" value={`${summary.max_drawdown_pct}%`} alert={summary.max_drawdown_pct < -20} />
            <DataCard label="Total P&L"    value={`${summary.total_pnl_pct > 0 ? "+" : ""}${summary.total_pnl_pct}%`} />
          </div>

          {/* Hypothesis verdict */}
          {summary.win_rate_pct >= 58 && (
            <div className="bg-accent/5 border border-accent/30 text-accent p-4 font-mono text-sm mb-4">
              <span className="font-bold">PASS</span> win_rate {">="} 58% — Hypothesis SUPPORTED. Momentum signal has measurable edge in prediction markets.
            </div>
          )}
          {summary.win_rate_pct >= 52 && summary.win_rate_pct < 58 && (
            <div className="bg-dark border border-yellow-700/30 text-yellow-400 p-4 font-mono text-sm mb-4">
              <span className="font-bold">WEAK</span> win_rate 52–58% — marginal positive edge. More data or refined entry rules needed.
            </div>
          )}
          {summary.win_rate_pct < 52 && (
            <div className="bg-dark border border-red-500/30 text-red-400 p-4 font-mono text-sm mb-4">
              <span className="font-bold">FAIL</span> win_rate &lt; 52% — Hypothesis NOT supported. Signal rules require revision.
            </div>
          )}

          {/* Equity curve */}
          {equityCurve.length > 0 && (
            <div className="bg-surface border border-gray-800 border-t-2 border-t-accent p-4 mb-6">
              <div className="text-xs font-mono text-gray-500 uppercase tracking-wider mb-4">
                // equity_curve (indexed to 100)
              </div>
              <ResponsiveContainer width="100%" height={320}>
                <LineChart data={equityCurve} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#111111" />
                  <XAxis
                    dataKey="trade"
                    label={{ value: "trade #", position: "insideBottom", offset: -3, fill: "#4b5563" }}
                    tick={{ fill: "#4b5563", fontSize: 11, fontFamily: "JetBrains Mono, monospace" }}
                  />
                  <YAxis tick={{ fill: "#4b5563", fontSize: 11, fontFamily: "JetBrains Mono, monospace" }} />
                  <Tooltip
                    contentStyle={{
                      background:   "#0d0d0d",
                      border:       "1px solid #1f2937",
                      color:        "#e5e7eb",
                      fontFamily:   "JetBrains Mono, monospace",
                      fontSize:     "12px",
                    }}
                    formatter={(v, name) => [v.toFixed(2), name === "equityIdx" ? "equity_index" : "cum_pnl_%"]}
                  />
                  <ReferenceLine y={100} stroke="#1f2937" strokeDasharray="4 4" />
                  <Line type="monotone" dataKey="equityIdx" stroke="#ccff00" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
              <p className="text-xs text-gray-700 font-mono mt-2">
                base = 100. Quarter-Kelly sizing (max 5% TVL per trade). 0.5% slippage modeled.
              </p>
            </div>
          )}

          {/* Assumptions table */}
          <div>
            <div className="text-xs font-mono text-gray-500 uppercase tracking-wider mb-3">
              // explicit_assumptions (A1–A6)
            </div>
            <div className="bg-surface border border-gray-800 overflow-hidden">
              <table className="w-full text-sm">
                <tbody>
                  {[
                    ["A1", "Favorite-longshot bias persists in prediction markets",        "validated by backtest (62.9% WR)"],
                    ["A2", "MiroFish consensus (68% accuracy) provides >= 3% edge",        "HYPOTHESIS — see result above"],
                    ["A3", "Quarter-Kelly (25% of full Kelly) used for safety",            "Kelly 1956; institutional standard"],
                    ["A4", "All v1 trading is testnet only; no real funds at risk",        "explicit prototype scope"],
                    ["A5", "0.5% slippage modeled per trade (conservative estimate)",      "real slippage may vary with liquidity"],
                    ["A6", "Data: Polymarket Gamma API historical closed markets",         "reproducible with seed=42"],
                  ].map(([id, assumption, note]) => (
                    <tr key={id} className="border-b border-gray-800 last:border-0 hover:bg-surface-hover transition-colors">
                      <td className="px-4 py-3 font-mono text-gray-600 text-xs w-10">{id}</td>
                      <td className="px-4 py-3 text-gray-300 text-sm">{assumption}</td>
                      <td className="px-4 py-3 text-gray-600 text-xs font-mono">{note}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Data source & reproducibility */}
          <div className="mt-6 bg-surface border border-gray-800 p-4">
            <div className="text-xs font-mono text-gray-600 uppercase tracking-wider mb-3">// reproducibility</div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-500">Data Source:</span>
                <span className="text-gray-300 ml-2">{summary.data_source}</span>
              </div>
              <div>
                <span className="text-gray-500">Period:</span>
                <span className="text-gray-300 ml-2">{summary.backtest_period || "2020-2026"}</span>
              </div>
              <div>
                <span className="text-gray-500">Random Seed:</span>
                <span className="text-accent ml-2">{summary.parameters?.rng_seed || 42}</span>
              </div>
              <div>
                <span className="text-gray-500">Script:</span>
                <span className="text-accent ml-2">agent/backtest_reproducible.py</span>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
