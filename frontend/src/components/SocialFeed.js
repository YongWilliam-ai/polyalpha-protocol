/**
 * SocialFeed.js — Live Signal Radar (quantitative terminal format)
 * Inspired by polyainews · simulated feed, no live API key required.
 */

import React, { useState, useEffect } from "react";

const SIGNALS = [
  {
    id: 1,
    timestamp: "13:04:21",
    source:    "PolyAI News",
    badge:     "SIGNAL",
    content:   "BTC just printed a +0.41% candle in 7 minutes. YES side of 15m market still at 54%. Momentum signal ACTIVE — market hasn't caught up yet.",
    confidence: 84,
    edge:       2.1,
  },
  {
    id: 2,
    timestamp: "12:58:07",
    source:    "runes_leo",
    badge:     "ALPHA",
    content:   "Three strategies killed this week. All three autopsy reports written. Dead strategies are more valuable than live ones — they tell you exactly why a path doesn't work. That's the framework.",
    confidence: 91,
    edge:       3.4,
  },
  {
    id: 3,
    timestamp: "12:50:12",
    source:    "PolyBro",
    badge:     "RISK",
    content:   "Reminder: Kelly criterion is a maximum, not a target. Quarter-Kelly is how serious quants actually size. Your edge estimate is never as good as you think it is.",
    confidence: 78,
    edge:       1.2,
  },
  {
    id: 4,
    timestamp: "12:43:05",
    source:    "Polymarket News",
    badge:     "VOLUME",
    content:   "Volume alert: BTC 15m high/low markets crossed $2.1M in 4 hours. Institutional flow is picking up significantly. #Polymarket #BTC",
    confidence: 66,
    edge:       0.8,
  },
  {
    id: 5,
    timestamp: "12:26:19",
    source:    "runes_leo",
    badge:     "ALPHA",
    content:   "Hypothesis H7_ETH_Breakout: 50 trades in, win rate 56.2%, max DD 8.3%. Still ALIVE. Empirical Kelly shrinking to 2.9% as post-rally uncertainty grows.",
    confidence: 73,
    edge:       2.8,
  },
  {
    id: 6,
    timestamp: "12:12:44",
    source:    "PolyAI News",
    badge:     "FILTER",
    content:   "News sentiment analysis: 7 bearish headlines in last 30 min. Signal filter triggered — skipping UP bets until macro clears. Discipline > FOMO.",
    confidence: 62,
    edge:      -0.4,
  },
  {
    id: 7,
    timestamp: "12:04:01",
    source:    "PolyBro",
    badge:     "ALPHA",
    content:   "Quant edge on binary markets: the key isn't picking the right outcome — it's finding markets where the crowd is systematically mispricing momentum. Polymarket is still early.",
    confidence: 79,
    edge:       1.9,
  },
];

const BADGE_CLS = {
  SIGNAL: "bg-orange-900/40 text-orange-400",
  ALPHA:  "bg-green-900/30 text-green-400",
  RISK:   "bg-yellow-900/30 text-yellow-400",
  VOLUME: "bg-blue-900/30 text-blue-400",
  FILTER: "bg-purple-900/30 text-purple-400",
};

export default function SocialFeed() {
  const [highlighted, setHighlighted] = useState(0);

  useEffect(() => {
    const id = setInterval(() => setHighlighted((h) => (h + 1) % SIGNALS.length), 12_000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="bg-surface border border-gray-800 rounded-lg overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-800">
        <div className="flex items-center gap-2">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-success opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-success"></span>
          </span>
          <span className="text-sm font-mono font-bold text-white">Live Signal Radar</span>
        </div>
        <span className="text-xs text-gray-600 font-mono">polyainews</span>
      </div>

      {/* Signal list */}
      <div className="h-[600px] overflow-y-auto custom-scrollbar">
        {SIGNALS.map((s, i) => (
          <div
            key={s.id}
            className={`border-b border-gray-800/50 p-4 hover:bg-gray-800/20 transition-colors animate-fade-in-up ${
              i === highlighted ? "border-l-2 border-l-accent bg-accent/5" : ""
            }`}
          >
            {/* Header row */}
            <div className="flex items-center gap-2 mb-2 flex-wrap">
              <span className="font-mono text-xs text-gray-500">{s.timestamp}</span>
              <span className="font-mono text-xs text-accent uppercase">{s.source}</span>
              <span className={`ml-auto px-2 py-0.5 rounded text-[10px] font-mono ${BADGE_CLS[s.badge] || "bg-gray-800 text-gray-300"}`}>
                {s.badge}
              </span>
            </div>
            {/* Content */}
            <p className="text-sm text-gray-300 leading-relaxed">{s.content}</p>
            {/* Quantitative metrics */}
            <div className="mt-2 text-xs font-mono text-gray-600 flex gap-4">
              <span>Confidence: <span className="text-gray-400">{s.confidence}%</span></span>
              <span>
                Edge:{" "}
                <span className={s.edge >= 0 ? "text-success" : "text-red-400"}>
                  {s.edge >= 0 ? "+" : ""}{s.edge}%
                </span>
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="text-[10px] font-mono text-warning text-center p-2 border-t border-gray-800">
        Simulated feed · No live API key required
      </div>
    </div>
  );
}
