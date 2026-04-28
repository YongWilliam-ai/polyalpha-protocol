/**
 * SocialFeed.js — Mock X (Twitter) market-alpha feed widget.
 * Inspired by polyainews and brief.day1 open-source social aggregators.
 * Uses simulated tweets since a live Twitter API key is not available.
 */

import React, { useState, useEffect } from "react";

const TWEETS = [
  {
    id: 1,
    handle: "@polyainews",
    name: "PolyAI News",
    initials: "PA",
    color: "#e05050",
    time: "1m",
    content:
      "BTC just printed a +0.41% candle in 7 minutes. YES side of 15m market still at 54%. Momentum signal ACTIVE — market hasn't caught up yet. #Polymarket",
    likes: 312,
    rts: 97,
    tag: "SIGNAL",
    tagColor: "#5a3adc",
  },
  {
    id: 2,
    handle: "@runes_leo",
    name: "runes_leo",
    initials: "RL",
    color: "#2a7a5a",
    time: "6m",
    content:
      "Three strategies killed this week. All three autopsy reports written. Dead strategies are more valuable than live ones — they tell you exactly why a path doesn't work. That's the framework.",
    likes: 203,
    rts: 61,
    tag: "ALPHA",
    tagColor: "#2a7a5a",
  },
  {
    id: 3,
    handle: "@polybroapp",
    name: "PolyBro",
    initials: "PB",
    color: "#7c3aed",
    time: "14m",
    content:
      "Reminder: Kelly criterion is a maximum, not a target. Quarter-Kelly is how serious quants actually size. Your edge estimate is never as good as you think it is.",
    likes: 445,
    rts: 134,
    tag: "RISK",
    tagColor: "#b45309",
  },
  {
    id: 4,
    handle: "@polymarket_news",
    name: "Polymarket News",
    initials: "PM",
    color: "#5a3adc",
    time: "21m",
    content:
      "Volume alert: BTC 15m high/low markets crossed $2.1M in 4 hours. Institutional flow is picking up significantly. #Polymarket #BTC",
    likes: 72,
    rts: 19,
    tag: "VOL",
    tagColor: "#0e7490",
  },
  {
    id: 5,
    handle: "@runes_leo",
    name: "runes_leo",
    initials: "RL",
    color: "#2a7a5a",
    time: "38m",
    content:
      "Hypothesis H7_ETH_Breakout: 50 trades in, win rate 56.2%, max DD 8.3%. Still ALIVE. Empirical Kelly shrinking to 2.9% as post-rally uncertainty grows.",
    likes: 156,
    rts: 44,
    tag: "ALPHA",
    tagColor: "#2a7a5a",
  },
  {
    id: 6,
    handle: "@polyainews",
    name: "PolyAI News",
    initials: "PA",
    color: "#e05050",
    time: "52m",
    content:
      "News sentiment analysis: 7 bearish headlines in last 30 min. Signal filter triggered — skipping UP bets until macro clears. Discipline > FOMO.",
    likes: 88,
    rts: 23,
    tag: "FILTER",
    tagColor: "#7c3aed",
  },
  {
    id: 7,
    handle: "@polybroapp",
    name: "PolyBro",
    initials: "PB",
    color: "#7c3aed",
    time: "1h",
    content:
      "Quant edge on binary markets: the key isn't picking the right outcome — it's finding markets where the crowd is systematically mispricing momentum. Polymarket is still early.",
    likes: 88,
    rts: 23,
    tag: "ALPHA",
    tagColor: "#2a7a5a",
  },
];

export default function SocialFeed() {
  const [highlighted, setHighlighted] = useState(0);

  // Cycle the "new tweet" highlight every 12 seconds
  useEffect(() => {
    const id = setInterval(() => {
      setHighlighted((h) => (h + 1) % TWEETS.length);
    }, 12_000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="social-feed">
      <div className="social-feed-header">
        <div className="social-feed-title">
          <span className="live-dot" />
          Live Market Alpha
        </div>
        <span className="social-feed-sub">Inspired by polyainews</span>
      </div>

      <div className="social-feed-list">
        {TWEETS.map((t, i) => (
          <div
            key={t.id}
            className={`tweet ${i === highlighted ? "tweet-new" : ""}`}
          >
            <div className="tweet-row">
              <div
                className="tweet-avatar"
                style={{ background: t.color }}
              >
                {t.initials}
              </div>
              <div className="tweet-body">
                <div className="tweet-meta-top">
                  <span className="tweet-name">{t.name}</span>
                  <span className="tweet-handle">{t.handle}</span>
                  <span className="tweet-time">· {t.time}</span>
                  <span
                    className="tweet-tag"
                    style={{ background: t.tagColor + "33", color: t.tagColor }}
                  >
                    {t.tag}
                  </span>
                </div>
                <p className="tweet-content">{t.content}</p>
                <div className="tweet-actions">
                  <span className="tweet-stat">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
                    </svg>
                    {t.likes}
                  </span>
                  <span className="tweet-stat">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/>
                    </svg>
                    {t.rts}
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="social-feed-footer">
        Simulated feed · No live API key required
      </div>
    </div>
  );
}
