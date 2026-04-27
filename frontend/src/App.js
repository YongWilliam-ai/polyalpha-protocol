import React, { useState } from "react";
import VaultPage from "./pages/VaultPage";
import PositionLogPage from "./pages/PositionLogPage";
import BacktestPage from "./pages/BacktestPage";
import PALPHAHubPage from "./pages/PALPHAHubPage";
import "./App.css";

const TABS = [
  { id: "vault",    label: "Vault",         icon: "🏦" },
  { id: "signals",  label: "AI Signal Log",  icon: "🤖" },
  { id: "backtest", label: "Backtest",       icon: "📊" },
  { id: "hub",      label: "PALPHA Hub",     icon: "⬡" },
];

export default function App() {
  const [activeTab, setActiveTab] = useState("vault");

  return (
    <div className="app">
      <header className="header">
        <div className="header-brand">
          <span className="brand-logo">⬡</span>
          <span className="brand-name">PolyAlpha Protocol</span>
          <span className="brand-badge">Testnet</span>
        </div>
        <nav className="tabs">
          {TABS.map((t) => (
            <button
              key={t.id}
              className={`tab-btn ${activeTab === t.id ? "active" : ""}`}
              onClick={() => setActiveTab(t.id)}
            >
              {t.icon} {t.label}
            </button>
          ))}
        </nav>
      </header>

      <main className="main">
        {activeTab === "vault"    && <VaultPage />}
        {activeTab === "signals"  && <PositionLogPage />}
        {activeTab === "backtest" && <BacktestPage />}
        {activeTab === "hub"      && <PALPHAHubPage />}
      </main>

      <footer className="footer">
        PolyAlpha v1.0 · ISOM3270 Final Project · William Yong, HKUST RMBI ·&nbsp;
        <a href="https://amoy.polygonscan.com" target="_blank" rel="noreferrer">Polygonscan Amoy</a>
      </footer>
    </div>
  );
}
