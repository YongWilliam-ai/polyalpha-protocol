import React, { useState, useEffect } from "react";

const LABEL_META = {
  SWARM_STRONG_BUY:  { color: "text-accent",   bg: "bg-accent/10",   border: "border-accent/40",   tag: "STRONG BUY" },
  SWARM_BUY:         { color: "text-accent",   bg: "bg-accent/5",    border: "border-accent/20",   tag: "BUY"        },
  SWARM_HOLD:        { color: "text-yellow-400",bg: "bg-yellow-900/20",border: "border-yellow-700/30",tag: "HOLD"      },
  SWARM_SELL:        { color: "text-red-400",  bg: "bg-red-950/40",  border: "border-red-500/30",  tag: "SELL"       },
  SWARM_STRONG_SELL: { color: "text-red-400",  bg: "bg-red-950",     border: "border-red-500/50",  tag: "STRONG SELL"},
};

function PersonaRow({ vote, index }) {
  const isYes  = vote.vote === "YES";
  const isAbst = vote.vote === "ABSTAIN";
  const barPct = isYes ? vote.confidence : isAbst ? 50 : 100 - vote.confidence;

  return (
    <div className="border-b border-gray-800/60 px-4 py-3 last:border-0 hover:bg-surface-hover transition-colors">
      <div className="flex items-center gap-2 mb-1.5">
        <span className="text-gray-600 font-mono text-xs w-5 shrink-0">P{index + 1}</span>
        <span className="font-mono text-sm text-white">{vote.persona}</span>
        <span className={`ml-auto font-mono text-xs font-bold px-2 py-0.5 border ${
          isAbst
            ? "text-gray-500 border-gray-700"
            : isYes
            ? "text-accent border-accent/40 bg-accent/5"
            : "text-red-400 border-red-500/40 bg-red-950/30"
        }`}>
          {vote.vote} @ {vote.confidence}%
        </span>
        <span className="font-mono text-xs text-gray-600 w-14 text-right shrink-0">
          w={vote.weight.toFixed(2)}
        </span>
      </div>

      {/* Confidence bar */}
      <div className="ml-7 h-0.5 bg-gray-800 mb-1.5 w-full overflow-hidden">
        <div
          className={`h-full transition-all duration-700 ${isYes ? "bg-accent" : "bg-red-500"}`}
          style={{ width: `${barPct}%` }}
        />
      </div>

      <p className="ml-7 text-xs text-gray-500 leading-relaxed">{vote.reasoning}</p>
    </div>
  );
}

export default function SwarmPanel() {
  const [data,    setData]    = useState(null);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState(null);

  useEffect(() => {
    fetch("/swarm_latest.json")
      .then((r) => {
        if (!r.ok) throw new Error("not found");
        return r.json();
      })
      .then((d) => { setData(d); setLoading(false); })
      .catch((e) => { setError(e.message); setLoading(false); });
  }, []);

  if (loading) {
    return (
      <div className="bg-surface border border-gray-800 p-6 font-mono text-sm text-gray-500 animate-pulse">
        {">"} initialising swarm...
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="bg-surface border border-gray-800 p-6">
        <div className="font-mono text-xs text-gray-600 mb-3 flex items-center gap-2">
          <span className="w-2 h-2 bg-gray-700 inline-block" />
          swarm_latest.json — not found
        </div>
        <p className="text-sm text-gray-500">
          No swarm data yet. Start the Python agent to generate consensus:
        </p>
        <code className="block mt-2 bg-dark border border-gray-800 px-3 py-2 text-xs font-mono text-accent">
          cd agent &amp;&amp; python pm_arb_agent.py --once
        </code>
      </div>
    );
  }

  const meta      = LABEL_META[data.label] || LABEL_META.SWARM_HOLD;
  const pct       = Math.round(data.consensus * 100);
  const yesVotes  = data.votes.filter((v) => v.vote === "YES").length;
  const noVotes   = data.votes.filter((v) => v.vote === "NO").length;

  return (
    <div className="bg-surface border border-gray-800">
      {/* Terminal header */}
      <div className="border-b border-gray-800 px-4 py-2.5 flex items-center gap-2">
        <span className="w-2 h-2 bg-accent inline-block" />
        <span className="font-mono text-xs text-gray-500">// mirofish_swarm.consensus</span>
        <span className={`ml-auto text-xs font-mono font-bold px-2 py-0.5 border ${meta.color} ${meta.bg} ${meta.border}`}>
          {meta.tag}
        </span>
        <span className={`text-xs font-mono px-1.5 py-0.5 ${data.source === "live" ? "text-accent" : "text-gray-500"}`}>
          [{data.source}]
        </span>
      </div>

      {/* Question */}
      <div className="px-4 pt-3 pb-2 border-b border-gray-800">
        <div className="text-xs font-mono text-gray-600 mb-1 uppercase tracking-wider">Market Question</div>
        <p className="text-sm text-white font-mono leading-relaxed">{data.market_question}</p>
      </div>

      {/* Consensus gauge */}
      <div className="px-4 py-4 border-b border-gray-800">
        <div className="flex items-end justify-between mb-2">
          <span className="text-xs font-mono text-gray-500 uppercase tracking-wider">Weighted Consensus (YES)</span>
          <span className="font-mono text-xs text-gray-500">{yesVotes}Y / {noVotes}N</span>
        </div>
        <div className="flex items-end gap-4">
          <span className={`text-5xl font-mono font-bold ${meta.color}`}>{pct}%</span>
          <span className={`text-sm font-mono font-semibold mb-1.5 ${meta.color}`}>{meta.tag}</span>
        </div>
        {/* Full-width gauge bar */}
        <div className="mt-3 h-1 bg-gray-800 w-full overflow-hidden">
          <div
            className="h-full bg-accent transition-all duration-1000"
            style={{ width: `${pct}%` }}
          />
        </div>
        <div className="flex justify-between mt-1">
          <span className="text-xs font-mono text-gray-700">0</span>
          <span className="text-xs font-mono text-gray-700">100</span>
        </div>
      </div>

      {/* Persona interview log */}
      <div className="px-0">
        <div className="px-4 py-2 border-b border-gray-800 flex items-center gap-2">
          <span className="text-xs font-mono text-gray-600">// persona_interview_log ({data.votes.length} analysts)</span>
        </div>
        {data.votes.map((vote, i) => (
          <PersonaRow key={vote.persona} vote={vote} index={i} />
        ))}
      </div>
    </div>
  );
}
