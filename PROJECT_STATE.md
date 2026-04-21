# PolyAlpha Protocol — Project State Log

> **用途**：這份文件是 William、Claude Code 和 Manus 三方的「共同記憶」。
> 每次 Claude Code 完成一個任務後，Manus 會更新這份文件。
> 每次給 Claude Code 新 Prompt 時，都會把這份文件的最新內容附在 Prompt 開頭。

---

## 當前狀態快照 (Last Updated: 2026-04-21)

### 整體進度

| 層級 | 狀態 | 說明 |
|---|---|---|
| GitHub Repo | ✅ 已建立 | `YongWilliam-ai/polyalpha-protocol` (private) |
| 合約：PolyAlphaVault.sol | ✅ 已完成 | ERC-4626 + logPosition() + circuit breaker |
| 合約：PALPHAToken.sol | ✅ 已完成 | 10M max supply ERC-20 (6 utility stubs) |
| 合約：MockUSDC.sol | ✅ 已完成 | Testnet USDC |
| 合約：ALPHAStakingPool.sol | ⏳ 待 Claude 寫 | 第一個 5 小時週期任務 |
| 合約：PALPHABuybackBurn.sol | ⏳ 待 Claude 寫 | 第一個 5 小時週期任務 |
| 合約：PolyAlphaDAO.sol | ⏳ 待 Claude 寫 | 第二個 5 小時週期任務 |
| Python Agent | ✅ 基礎已完成 | btc_signal.py + agent.py + backtest.py |
| Python Agent (升級) | ⏳ 待 Claude 升級 | 雙源預言機 + 蒙特卡洛 Kelly |
| 前端 Dashboard | ✅ 骨架已完成 | VaultPage, PositionLogPage, BacktestPage |
| 前端 $PALPHA Hub | ⏳ 待 Manus 建 | 質押/治理/回購頁面 |
| Amoy 部署 | ⏳ 待 William 執行 | npm run compile 已修復，等待 npm run deploy:amoy |
| 回測報告 | ⏳ 待執行 | python backtest.py |

---

## 已完成的關鍵決策與修復記錄

### 2026-04-21 凌晨 1:41 — Claude Code 完成 V2.0 初始建置
Claude Code 在 Claude.ai 介面中完成了以下工作：
- 建立了完整的 `contracts/` 目錄（Vault, Token, MockUSDC）
- 建立了 `agent/` 目錄（btc_signal.py, agent.py, backtest.py, test_connection.py）
- 建立了 `frontend/` 目錄（React 骨架，3 個頁面）
- 建立了 `scripts/deploy.js`、`hardhat.config.js`、`SETUP.md`
- **重要決策**：GPT-4o 從 BTC 信號中移除，改用 Binance 動量規則（避免 API 成本）
- **重要決策**：Becker dataset 聲明修正為「8,700+ markets」（非 400M）

### 2026-04-21 上午 (Round 3) — Manus 修復 mcopy opcode 錯誤
- **修復 Bug 3**：`hardhat.config.js` 的 Solidity 版本升級到 `0.8.25` 並加入 `evmVersion: "cancun"`
  - 原因：OpenZeppelin v5 的 `Memory.sol` 使用了 `mcopy` opcode，這是 EVM Cancun 升級（EIP-5656）才引入的指令，需要 Solidity 0.8.25 + `evmVersion: cancun`
  - 修復已推送到 GitHub main branch
- **重要技術規格更新**：Solidity 版本 = `0.8.25`，evmVersion = `cancun`（不能改！）

### 2026-04-21 上午 (Round 2) — Manus 修復 Unicode 字符編譯錯誤
- **修復 Bug 2**：`PALPHAToken.sol` 和 `PolyAlphaVault.sol` 中有大量 Unicode 字符（`—` em dash、`─` box drawing、`×` multiply、`≥` greater-equal）
  - Solidity 編譯器不接受字串中的非 ASCII 字符
  - 已用 Python 腳本掃描並替換全部 3 個合約文件中的所有非 ASCII 字符
  - 修復已推送到 GitHub main branch
- **當前狀態**：`npm run compile` 應可成功，等待 William 執行驗證

### 2026-04-21 上午 (Round 1) — Manus 完成 GitHub 遷移與 Bug 修復
- 在 GitHub 建立了私有 repo `YongWilliam-ai/polyalpha-protocol`
- 建立了 `.gitignore`、`README.md`、`scripts/auto-push.sh`、`package.json`
- **修復 Bug**：`hardhat.config.js` 的 Solidity 版本從 `0.8.20` 升級到 `0.8.24`
  - 原因：OpenZeppelin v5 的 `ERC4626.sol` 和 `Memory.sol` 要求 `^0.8.24`
  - 修復已推送到 GitHub main branch
- William 已成功執行 `npm install`（579 packages installed）
- William 需要執行 `git pull` 後再次嘗試 `npm run compile`

---

## 當前文件結構

```
polyalpha-protocol/
├── contracts/
│   ├── PolyAlphaVault.sol      ✅ ERC-4626 vault + logPosition() + circuit breaker
│   ├── PALPHAToken.sol         ✅ 10M max supply ERC-20
│   └── MockUSDC.sol            ✅ Testnet USDC
├── scripts/
│   ├── deploy.js               ✅ Hardhat deploy script
│   └── auto-push.sh            ✅ Auto git push script
├── agent/
│   ├── btc_signal.py           ✅ 7-min BTC momentum signal
│   ├── agent.py                ✅ Main scan → signal → log loop
│   ├── backtest.py             ✅ Historical backtester
│   └── test_connection.py      ✅ Connection tester
├── frontend/
│   └── src/pages/
│       ├── VaultPage.js        ✅ TVL stats + deposit/withdraw
│       ├── PositionLogPage.js  ✅ On-chain signal log
│       └── BacktestPage.js     ✅ Equity curve chart
├── hardhat.config.js           ✅ FIXED: Solidity 0.8.24
├── package.json                ✅ npm scripts configured
├── .env.example                ✅ Template (William needs to fill .env)
├── .gitignore                  ✅
├── README.md                   ✅
└── SETUP.md                    ✅ Day-by-Day execution guide
```

---

## 下一步行動清單

### William 需要做（按順序）
1. `git pull origin main --rebase` — 拉取 Manus 修復的 hardhat.config.js
2. `npm run compile` — 驗證編譯成功
3. 填寫 `.env` 文件（PRIVATE_KEY, AMOY_RPC_URL, POLYGONSCAN_API_KEY）
4. `npm run deploy:amoy` — 部署到 Polygon Amoy 測試網
5. 把合約地址填回 `.env`

### Claude Code 需要做（第一個 5 小時週期）
- 寫 `ALPHAStakingPool.sol`
- 寫 `PALPHABuybackBurn.sol`

### Manus 需要做（等 Claude 完成合約後）
- 建立前端 `$PALPHA Hub` 頁面（質押/治理/回購）
- 更新 `frontend/src/config.js` 加入新合約地址

---

## 重要技術規格（Claude Code 必須遵守）

- **Solidity 版本**：`0.8.25`（不能用 0.8.20/0.8.24！OpenZeppelin v5 Memory.sol 的 mcopy opcode 需要 0.8.25）
- **EVM 版本**：`cancun`（不能省略！mcopy 是 EIP-5656 Cancun 指令）
- **OpenZeppelin 版本**：v5（已安裝）
- **測試網**：Polygon Amoy（chainId: 80002）
- **Token 供應量**：10M max supply，3M initial mint（不能改）
- **Agent 模式**：Dry-run 模式（VAULT_CONTRACT_ADDRESS 未設定時自動啟用）
- **信號引擎**：Binance 動量規則（不用 GPT-4o，避免 API 成本）
