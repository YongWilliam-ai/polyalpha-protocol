import React, { useState } from "react";
import VaultPage       from "./pages/VaultPage";
import PositionLogPage from "./pages/PositionLogPage";
import BacktestPage    from "./pages/BacktestPage";
import PALPHAHubPage   from "./pages/PALPHAHubPage";
import "./App.css";

const TABS = [
  { id: "vault",    label: "Vault"        },
  { id: "signals",  label: "AI Signal Log" },
  { id: "backtest", label: "Backtest"      },
  { id: "hub",      label: "PALPHA Hub"    },
];

export default function App() {
  const [activeTab, setActiveTab] = useState("vault");

  return (
    <div className="min-h-screen flex flex-col bg-dark text-gray-200 font-sans">
      {/* Sticky nav */}
      <nav className="sticky top-0 z-50 backdrop-blur-md bg-dark/80 border-b border-gray-800">
        <div className="max-w-[1200px] mx-auto px-6 flex items-center justify-between h-14">
          <div className="flex items-center gap-2">
            <span className="text-accent text-xl font-bold">⬡</span>
            <span className="text-xl font-bold tracking-tight text-white">PolyAlpha Protocol</span>
            <span className="text-xs bg-gray-800 text-gray-400 px-2 py-0.5 rounded font-mono">Testnet</span>
          </div>
          <div className="flex items-center gap-1">
            {TABS.map((t) => (
              <button
                key={t.id}
                onClick={() => setActiveTab(t.id)}
                className={`px-4 py-1.5 text-sm transition-colors border-b-2 ${
                  activeTab === t.id
                    ? "text-white border-accent"
                    : "text-gray-400 hover:text-accent border-transparent"
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>
        </div>
      </nav>

      <main className="flex-1 max-w-[1200px] w-full mx-auto px-6 py-6">
        {activeTab === "vault"    && <VaultPage />}
        {activeTab === "signals"  && <PositionLogPage />}
        {activeTab === "backtest" && <BacktestPage />}
        {activeTab === "hub"      && <PALPHAHubPage />}
      </main>

      <footer className="text-center py-3 text-xs text-gray-600 border-t border-gray-800/50 font-mono">
        PolyAlpha v1.0 · ISOM3270 Final Project · William Yong, HKUST RMBI ·{" "}
        <a
          href="https://amoy.polygonscan.com"
          target="_blank"
          rel="noreferrer"
          className="text-accent hover:underline"
        >
          Polygonscan Amoy
        </a>
      </footer>
    </div>
  );
}
