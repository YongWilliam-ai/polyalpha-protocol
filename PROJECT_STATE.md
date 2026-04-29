# PolyAlpha Protocol — Project State Log

> **用途**：這份文件是 William、Claude Code 和 Manus 三方的「共同記憶」。
> 每次 Claude Code 完成一個任務後，Manus 會更新這份文件。
> 每次給 Claude Code 新 Prompt 時，都會把這份文件的最新內容附在 Prompt 開頭。

---

## 當前狀態快照 (Last Updated: 2026-04-29)

### 整體進度

| 層級 | 狀態 | 說明 |
|---|---|---|
| GitHub Repo | ✅ 已建立 | `YongWilliam-ai/polyalpha-protocol` (private) |
| 合約部署 | ✅ 6 個合約已全數部署 | 部署於 ChainLab Testnet (chainId: 31337) |
| Python Agent | ✅ Paper Trading 模式運行中 | 具備 Polymarket/CEX 數據抓取與 6 步安全檢查 |
| 回測系統 | ✅ 已執行 | `backtest.py` 支援 synthetic demo 數據與資金曲線生成 |
| 前端 Dashboard | ✅ 已完成 4 大核心頁面 | Vault, AI Signal Log, Backtest, PALPHA Hub |
| 開源策略整合 | 🔄 進行中 | 準備讓 Claude Code 讀取 19 個 GitHub/X 連結並提取 Alpha |

---

## 已部署合約地址（ChainLab Testnet, chainId: 31337）

| 合約 | 地址 |
|---|---|
| MockUSDC | `0x77D7D52eE789B7C6bcD94eb87e2391BBb94A8D0a` |
| PALPHAToken | `0x36381Cd13C9030Eb7dfa7C274837115370FEcdbF` |
| PolyAlphaVault | `0x1c275054C7159aBBF446E652A744EFB8cbf6efd0` |
| ALPHAStakingPool | `0xF8E9E3af72E1F673B21eCB4d96C99BF9c1D47832` |
| PALPHABuybackBurn | `0xEc33dBc9dFAa1c380863547C5bCB7597eD611Ea4` |
| PolyAlphaDAO | `0x03C56c5bFc857694ECfdfCCa49456d67340E2BF0` |

> **注意**：舊文件中的「Polygon Amoy」已全面遷移至「ChainLab Testnet」。

---

## 重要技術規格（Claude Code 必須遵守）

- **Solidity 版本**：`0.8.25`（不能用 0.8.20/0.8.24！）
- **EVM 版本**：`cancun`（不能省略！mcopy 是 EIP-5656 Cancun 指令）
- **OpenZeppelin 版本**：v5（已安裝）
- **測試網**：ChainLab Testnet（chainId: 31337）
- **Agent 模式**：目前為 Paper Trading，後續將切換至 Dry-run（連上真實 API 測滑點）
- **ASCII only**：所有 .sol 文件不能有 Unicode 字符

---

## 已完成清單：Phase 1 (Dry-Run Mode Strategies)
- [x] 整合 19 個開源資源並生成 `OpenSource_Integration_Plan.md`
- [x] 實作 `yes_no_arb_scanner` (YES+NO < $1.00 無風險套利)
- [x] 實作 `correlation_arb_scanner` (邏輯矛盾套利)
- [x] 實作 `get_macro_sentiment` (6551Team/daily-news 新聞情緒閘門)

## 下一步行動清單：Phase 2 (Demo Preparation)
William 的專案已 100% 完成代碼開發，現在進入期末報告與 Demo 準備階段：
1. 撰寫 **PolyAlpha Startup Pitch Deck**（給教授看的投影片大綱或完整簡報）
2. 撰寫 **Technical Architecture Document**（詳細說明 AI Agent、Smart Contracts 和 Execution Engine 的協同架構）
3. 製作系統架構圖（展示 paper_mode 安全測試策略與 Live 模式切換流程）
