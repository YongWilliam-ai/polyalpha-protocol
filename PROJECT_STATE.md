# PolyAlpha Protocol — Project State Log

> **用途**：這份文件是 William、Claude Code 和 Manus 三方的「共同記憶」。
> 每次 Claude Code 完成一個任務後，Manus 會更新這份文件。
> 每次給 Claude Code 新 Prompt 時，都會把這份文件的最新內容附在 Prompt 開頭。

---

## 當前狀態快照 (Last Updated: 2026-04-27)

### 整體進度

| 層級 | 狀態 | 說明 |
|---|---|---|
| GitHub Repo | ✅ 已建立 | `YongWilliam-ai/polyalpha-protocol` (private) |
| npm run compile | ✅ 已成功 | Compiled 26 Solidity files successfully (evm target: cancun) |
| 合約：PolyAlphaVault.sol | ✅ 已完成 | ERC-4626 + logPosition() + circuit breaker |
| 合約：PALPHAToken.sol | ✅ 已完成 | 10M max supply ERC-20 |
| 合約：MockUSDC.sol | ✅ 已完成 | Testnet USDC |
| 合約：ALPHAStakingPool.sol | ✅ 已完成 | Synthetix-style 10% APY |
| 合約：PALPHABuybackBurn.sol | ✅ 已完成 | depositForBurn() + executeBurn() |
| 合約：PolyAlphaDAO.sol | ✅ 已完成並部署 | `0x03C56c5bFc857694ECfdfCCa49456d67340E2BF0` (ChainLab) |
| 部署網絡 | ✅ ChainLab Testnet | chainId: 31337, RPC: https://testnet.chainlab.fun |
| 部署狀態 | ✅ 5 個合約已部署 | 見下方地址 |
| Python Agent | ✅ V2 已升級 | dual_source_oracle_check() + monte_carlo_kelly() |
| 前端 Dashboard | ✅ 已配置合約地址 | 3 個頁面 + config.js 已填入地址 |
| 前端 $PALPHA Hub | ✅ 已完成 | Staking / Governance / Buyback & Burn 3 個 section |
| 回測報告 | ✅ 已執行 | synthetic demo 數據已生成 |
| Polygonscan API Key | ✅ 已設定 | ACE4F5VKZJYRCW8MHWGZ816W9ZI5VPCQJ9 |

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

> **注意**：部署在 ChainLab Testnet（非 Polygon Amoy）。如需部署到 Amoy，使用 `npm run deploy:amoy`。

---

## 環境變數（已設定）

| 變數 | 值 |
|---|---|
| PRIVATE_KEY | `7d9d78a502311391d25a8a6f9be0f5f74032d55dd5687c2f512bfcf7dd7717eb` |
| POLYGONSCAN_API_KEY | `ACE4F5VKZJYRCW8MHWGZ816W9ZI5VPCQJ9` |
| AMOY_RPC_URL | `https://rpc-amoy.polygon.technology/` |
| CHAINLAB_RPC_URL | `https://testnet.chainlab.fun` |

---

## 重要技術規格（Claude Code 必須遵守）

- **Solidity 版本**：`0.8.25`（不能用 0.8.20/0.8.24！）
- **EVM 版本**：`cancun`（不能省略！mcopy 是 EIP-5656 Cancun 指令）
- **OpenZeppelin 版本**：v5（已安裝）
- **測試網**：ChainLab Testnet（chainId: 31337）已部署；Polygon Amoy（chainId: 80002）備用
- **Token 供應量**：10M max supply，3M initial mint（不能改）
- **Agent 模式**：Dry-run 模式（VAULT_CONTRACT_ADDRESS 未設定時自動啟用）
- **信號引擎**：Binance 動量規則（不用 GPT-4o，避免 API 成本）
- **ASCII only**：所有 .sol 文件不能有 Unicode 字符（em dash, box drawing 等）

---

## Polymarket V2 遷移注意事項（2026-04-22 已上線）

- V1 已棄用，V2 使用 pUSD（而非 USDC.e）作為抵押品
- Python Agent 如需直接連接 Polymarket，必須使用 `py-clob-client-v2`
- 新訂單結構：移除 `nonce/feeRateBps`，新增 `timestamp/builder`
- 新 Exchange 合約地址：`0xE111180000d2663C0091e4f400237545B87B996B`
- **對我們的影響**：Vault 合約本身不受影響（我們用 MockUSDC 模擬）；Agent 的 Polymarket 數據獲取需要升級

---

## 當前文件結構

```
polyalpha-protocol/
├── contracts/
│   ├── PolyAlphaVault.sol      ✅ ERC-4626 vault + logPosition() + circuit breaker
│   ├── PALPHAToken.sol         ✅ 10M max supply ERC-20
│   ├── MockUSDC.sol            ✅ Testnet USDC
│   ├── ALPHAStakingPool.sol    ✅ 10% APY staking
│   ├── PALPHABuybackBurn.sol   ✅ depositForBurn + executeBurn
│   └── PolyAlphaDAO.sol        ✅ 48h timelock governance (deployed)
├── scripts/
│   ├── deploy.js               ✅ 部署 5 個合約
│   ├── deployDAO.js            ✅ 專門部署 PolyAlphaDAO
│   └── auto-push.sh            ✅ Auto git push script
├── agent/
│   ├── btc_signal.py           ✅ V2: dual_source_oracle + monte_carlo_kelly
│   ├── agent.py                ✅ Main scan → signal → log loop
│   ├── backtest.py             ✅ Historical backtester
│   └── test_connection.py      ✅ Connection tester
├── frontend/
│   └── src/
│       ├── config.js           ✅ 6 個合約地址已填入（含 DAO）
│       ├── App.js              ✅ 4 個 Tab 導航（含 PALPHA Hub）
│       └── pages/
│           ├── VaultPage.js        ✅ TVL stats + deposit/withdraw
│           ├── PositionLogPage.js  ✅ On-chain signal log
│           ├── BacktestPage.js     ✅ Equity curve chart
│           └── PALPHAHubPage.js    ✅ Staking / Governance / Buyback & Burn (425 lines)
├── hardhat.config.js           ✅ Solidity 0.8.25 + cancun + ChainLab network
├── package.json                ✅ npm scripts configured
├── .env                        ✅ 已填入所有環境變數
├── .gitignore                  ✅
├── README.md                   ✅
└── SETUP.md                    ✅
```

---

## 下一步行動清單

### William 需要做（按順序）
1. 開一個新的 Claude Code 對話，把「Claude Code 第四週期 Prompt」貼給 Claude Code 執行
2. 執行完畢後，執行 `git push` 並回報 Manus

### Claude Code 需要做（第四週期）
- 升級 Python Agent：polymarket-toolkit V2 數據獲取
- 加入 daily-news MCP 情緒過濾器
- 升級 Monte Carlo Kelly 為 Empirical Kelly
- 確認 6 步安全檢查鏈已在 agent.py 主迴圈中

### Manus 需要做（等 William push 後）
- 審查 Python Agent 升級代碼
- 開始準備 Final PDF Report 和 Demo Video 資料

---

## Claude Code 第三週期 Prompt（DAO 部署 + $PALPHA Hub 前端）

```text
[CONTEXT & MEMORY - Read this carefully before starting]

Project: PolyAlpha Protocol (ISOM3270 Final Project)
Working Directory: C:\Users\user\Desktop\Dev.items.folder\ISOM3270_Startup
GitHub: YongWilliam-ai/polyalpha-protocol (private)

== What has happened so far ==
1. All 5 core contracts are DEPLOYED to ChainLab Testnet.
2. Manus (the QA AI) has successfully fixed the `backtest.py` script. The `--source dummy` mode now correctly generates `backtest_summary.json` and `equity_curve.csv` with synthetic demo data.
3. William has pulled the fix and generated the files for the frontend.
4. The frontend Backtest page is now working perfectly.

== Current Task Goal ==
We need to complete the final smart contract (`PolyAlphaDAO.sol`), deploy it, and build the final frontend page (`PALPHAHubPage.js`) for staking, governance, and buyback history.

[TASK 1: Write and Deploy PolyAlphaDAO.sol]
Write `contracts/PolyAlphaDAO.sol` with the following specs:
- `createProposal(string description, address targetContract, bytes callData)` → requires proposer to hold >= 1,000 PALPHA
- `vote(uint256 proposalId, bool support)` → 1 PALPHA = 1 vote, snapshot at proposal creation
- `executeProposal(uint256 proposalId)` → only after 48-hour timelock AND quorum met AND majority YES
- `cancelProposal(uint256 proposalId)` → only by original proposer, only if not yet executed
- Voting period: 48 hours from proposal creation
- Quorum: minimum 100,000 PALPHA total votes
- ASCII-only in comments and strings (NO Unicode chars)
- Solidity 0.8.25, OpenZeppelin v5

Then, update `scripts/deploy.js` to deploy PolyAlphaDAO as step 6 (args: PALPHAToken address).
Run the deployment script on ChainLab Testnet (`npm run deploy:chainlab` or `npx hardhat run scripts/deploy.js --network chainlab`).
Save the deployed DAO address.

[TASK 2: Update Frontend Config]
Update `frontend/src/config.js`:
- Add `export const DAO_ADDRESS = "your_deployed_address";`
- Add `export const DAO_ABI = [ ... ];` with the necessary functions (createProposal, vote, executeProposal, etc.).

[TASK 3: Build PALPHAHubPage.js]
Create `frontend/src/pages/PALPHAHubPage.js`. This page should have 3 sections (can use tabs or vertical layout):
1. **Staking**: Show user's staked balance, earned rewards, and total staked in the pool. Provide Stake/Unstake/Claim buttons (connect to `STAKING_ADDRESS`).
2. **Governance**: List active/past proposals (can use mock data if no events exist yet) and provide a "Create Proposal" button (connect to `DAO_ADDRESS`).
3. **Buyback & Burn**: Show `totalAlphaBurned` and `pendingBurn` from the `BUYBACK_ADDRESS` contract.

Update `frontend/src/App.js` to include this new page as the 4th tab in the navigation.

[CONSTRAINTS - Do NOT violate]
- Solidity: exactly 0.8.25 (no caret ^)
- evmVersion: cancun (in hardhat.config.js, do NOT change)
- OpenZeppelin v5 only
- ASCII-only in ALL .sol files
- Do NOT modify PolyAlphaVault.sol, PALPHAToken.sol, or any already-deployed contract

[WORKFLOW]
1. Complete all 3 tasks.
2. Run `npm run compile` to ensure contracts compile.
3. Run `cd frontend && npm run build` to ensure React compiles.
4. Tell William: "DAO contract deployed and PALPHA Hub page built. Please run:
git add -A
git commit -m 'feat: deploy DAO and build PALPHA Hub frontend'
git push origin main"
```

---

## runes_leo 踩坑記錄洞見 (Added 2026-04-27)

來源：https://x.com/runes_leo/status/2044009023713022094

### 核心元規則（Claude Code 必須理解）

1. **H = Hypothesis（假設）**：每個策略都是一個假設，85% 的假設會死。不要情感綁定。
2. **死的策略比活的更有價值**：死因分析 > 成功策略。每次策略失敗，必須寫 Autopsy Report。
3. **Paper Trading ≠ Live Trading**：跟單「聰明錢」Paper 賺 77%，實盤虧 74%。滑點和延遲是殺手。
4. **官方 API 的 PnL 計算有 Bug**：18.3% 的交易記錄是假的。必須用現金流模型計算 PnL。
5. **正收益是減出來的**：學會停止虧損策略，比尋找新策略更重要。

### 死亡判定標準（Kill Criteria）
- 連續 50 筆交易後，勝率 < 52% → KILL
- Max Drawdown 超過 15% → KILL
- 實盤與 Paper 的 PnL 偏差超過 20% → PAUSE & REVIEW

### 當前策略假設
- **H1_BTC_Momentum**：BTC 15分鐘動量領先 Polymarket 賠率變化（待回測驗證）

---

## Claude Code 第四週期 Prompt（Python Agent 開源整合）

> **注意**：開一個全新的 Claude Code 對話再貼此 Prompt，保持任務清晰。

```text
[CONTEXT & MEMORY - Read this carefully before starting]

Project: PolyAlpha Protocol (ISOM3270 Final Project)
Working Directory: C:\Users\user\Desktop\Dev.items.folder\ISOM3270_Startup
GitHub: YongWilliam-ai/polyalpha-protocol (private)

== What has been completed ==
1. All 6 contracts deployed to ChainLab Testnet:
   - MockUSDC:          0x77D7D52eE789B7C6bcD94eb87e2391BBb94A8D0a
   - PALPHAToken:       0x36381Cd13C9030Eb7dfa7C274837115370FEcdbF
   - PolyAlphaVault:    0x1c275054C7159aBBF446E652A744EFB8cbf6efd0
   - ALPHAStakingPool:  0xF8E9E3af72E1F673B21eCB4d96C99BF9c1D47832
   - PALPHABuybackBurn: 0xEc33dBc9dFAa1c380863547C5bCB7597eD611Ea4
   - PolyAlphaDAO:      0x03C56c5bFc857694ECfdfCCa49456d67340E2BF0
2. Frontend React dashboard: 4 pages (Vault, AI Signal Log, Backtest, PALPHA Hub)
3. Backtest output files (synthetic demo) already in frontend/public/
4. Python Agent currently uses basic momentum rules + theoretical Kelly sizing

== Current Task Goal ==
Upgrade the Python Agent (agent.py, btc_signal.py, backtest.py) by integrating
3 open-source resources to improve data quality, risk management, and PnL accuracy.

[TASK 1: Data Fetching Layer — Update agent.py & btc_signal.py]
1a. Add a function `get_polymarket_v2_odds(market_id)` in btc_signal.py:
    - Primary: use runesleo/polymarket-toolkit logic (V2 compatible)
    - Fallback: use Gamma API (https://gamma-api.polymarket.com/markets/{id})
    - If polymarket-toolkit is not installed, write as a stub with TODO comment

1b. Add a function `get_news_sentiment()` in agent.py:
    - Call: https://ai.6551.io/open/free_hot?category=crypto (no API key needed)
    - Parse the response and return "bullish", "bearish", or "neutral"
    - Use this as a pre-filter: skip trade if sentiment is "bearish" and signal is UP
    - Comment: "# Inspired by 6551Team/daily-news MCP Server"

[TASK 2: Risk Management Layer — Update btc_signal.py]
Upgrade `monte_carlo_kelly()` to `empirical_kelly()`:
    - Instead of using a fixed theoretical win_rate, use the ACTUAL win rate from
      the last N trades stored in a rolling window (default N=50)
    - If fewer than 10 trades in history, fall back to monte_carlo_kelly()
    - Add a parameter `trade_history: list[dict]` (list of past {"won": bool} records)
    - Comment: "# Inspired by @RohOnChain Empirical Kelly research"

[TASK 3: Strategy Evaluation Layer — Verify backtest.py]
Review backtest.py and confirm:
    - The PnL calculation uses the cash-flow model (cost = bet_size, payout = shares * 1.0 if won)
    - NOT the simple odds difference (close_price - open_price)
    - Add a comment block at the top of run_backtest() explaining the runes_leo method
    - If the cash-flow model is already implemented, just add/improve the comment

[CONSTRAINTS]
- Do NOT modify any Solidity contracts (.sol files) or deployment scripts
- Do NOT change hardhat.config.js
- Ensure all new Python code has comments explaining which open-source resource inspired it
- If any SDK is not installed locally, write as a production-ready stub with TODO comment

[WORKFLOW]
1. Complete all 3 tasks.
2. Run: python agent\backtest.py --source dummy (should still pass Kill Criteria test)
3. Tell William: "Agent upgrade complete. Please run:
git add -A
git commit -m 'feat: Python Agent V2 upgrade - polymarket-toolkit + empirical kelly + news sentiment'
git push origin main"
```
