# PolyAlpha Protocol — 完整同步狀態報告
> 更新時間：2026-05-05 | 由 Manus AI 產出

---

## 一、同步總覽

| 分類 | 數量 | 狀態 | 需要行動的人 |
|---|---|---|---|
| **完全一致 (MATCH)** | 28 | ✅ 無需處理 | — |
| **GitHub 較新** | 6 | ✅ Manus 已確認，本地需 `git pull` | William |
| **本地較新（Claude Code 工作成果）** | 32 | ⚠️ 需要 William `git push` | William |
| **本地較新（文件/設定）** | 4 | ⚠️ 需要 William `git push` | William |
| **僅 GitHub 有（Manus 新增）** | 7 | ✅ 已在 GitHub，本地需 `git pull` | William |
| **已歸檔（移至 docs/archive）** | 4 | ✅ Manus 已處理 | — |
| **雜訊（node_modules/.venv 等）** | 61,500+ | ✅ 已在 .gitignore，無需處理 | — |

---

## 二、Manus 已完成的工作（GitHub 已更新）

以下文件 Manus 已直接在 GitHub 上更新，**你只需要執行 `git pull` 就能拿到**：

| 文件 | 說明 |
|---|---|
| `PolyAlpha Protocol — Complete Revised Project.md` | 整合最新 Phase 2 內容（+1096B） |
| `PolyAlpha_AI_Workflow_SOP.md` | 更新 SOP 流程（+866B） |
| `PolyAlpha_Daily_Todo_Sprint.md` | 更新 Sprint 任務（+728B） |
| `CLAUDE.md` | 更新給 Claude Code 的指令（+693B） |
| `PROJECT_STATE.md` | 更新最新專案狀態（+379B） |
| `.env.example` | 新增 LLM_API_KEY 和 ZEP_API_KEY 佔位符（+536B） |
| `PolyAlpha_6_OpenSource_REAL_Integration_Prompt.md` | 🆕 真實整合 Prompt（新增） |
| `PolyAlpha_Phase2_EdgeBuild_MiroFish_Prompt.md` | 🆕 Phase 2 完整 Prompt（新增） |
| `docs/Qlib_Evaluation_Report_PolyAlpha.md` | 🆕 Qlib 評估報告（新增） |
| `docs/Vercel_Deployment_Guide.md` | 🆕 Vercel 部署指南（新增） |
| `docs/architecture.png` | 🆕 架構圖（新增） |
| `docs/archive/` | 🆕 歸檔舊版 Prompt（6 個文件） |
| `.gitignore` | 新增 swarm_latest.json 排除規則 |

---

## 三、本地較新的文件（需要 William 執行 `git push`）

這些文件是 **Claude Code 的工作成果**，目前只在你的本地電腦，**必須 push 到 GitHub**：

### 🔴 最重要（Claude Code 的核心功能代碼）

| 文件 | 大小差異 | 說明 |
|---|---|---|
| `agent/pm_arb_agent.py` | +6577B | MiroFish Swarm 整合核心 |
| `agent/backtest.py` | +3356B | 現金流 PnL 計算 |
| `frontend/src/pages/VaultPage.js` | +1951B | EdgeBuild UI 升級 |
| `frontend/src/App.css` | +1311B | EdgeBuild 風格樣式 |
| `agent/arb_scanner.py` | +903B | 套利掃描器更新 |
| `agent/btc_signal.py` | +767B | BTC 信號邏輯更新 |
| `frontend/src/pages/BacktestPage.js` | +588B | 回測頁面更新 |
| `frontend/src/pages/PALPHAHubPage.js` | +553B | Hub 頁面更新 |
| `agent/agent.py` | +701B | 主 Agent 更新 |
| `agent/requirements.txt` | +68B | 新增 httpx 等依賴 |
| `frontend/public/index.html` | +306B | 首頁更新 |
| `frontend/tailwind.config.js` | +215B | Tailwind 設定更新 |
| `contracts/PolyAlphaVault.sol` | +234B | Vault 合約更新 |
| `contracts/PALPHAToken.sol` | +155B | Token 合約更新 |
| `frontend/src/components/DataCard.js` | +37B | DataCard 更新 |
| `frontend/src/config.js` | +85B | 前端設定更新 |

### 🟡 新增文件（LOCAL_ONLY，需要 `git add` 後 push）

| 文件 | 大小 | 說明 |
|---|---|---|
| `frontend/src/components/SwarmPanel.js` | 6232B | 🆕 MiroFish Swarm UI 面板 |
| `frontend/public/swarm_latest.json` | 2177B | 🆕 Swarm 模擬數據（已加入 .gitignore，不需要 push） |

### 🟢 文件/設定類（也需要 push）

| 文件 | 說明 |
|---|---|
| `package-lock.json` | npm install 結果 |
| `prompt_B.txt` | Prompt 更新 |
| `OpenSource_Integration_Plan.md` | 整合計劃更新 |
| `PolyAlpha_Roadmap_and_Prompts.md` | Roadmap 更新 |
| `PolyAlpha_Project_Review_and_Profit_Roadmap.md` | 利潤路線圖更新 |
| `PolyAlpha_Profit_Strategy_Prompt.md` | 策略 Prompt 更新 |
| `README.md` | README 更新 |
| `PolyAlpha_6_OpenSource_Audit_Report.md` | 審計報告更新 |
| `.gitignore` | 已由 Manus 更新並 push |
| `.claude/settings.local.json` | Claude 設定更新 |
| `.claude/mcp.json` | MCP 設定更新 |
| `scripts/deployDAO.js` | 部署腳本更新 |
| `scripts/auto-push.sh` | 自動推送腳本更新 |

---

## 四、William 需要執行的完整指令（一次性同步）

請在 VS Code 終端機（路徑：`C:\Users\user\Desktop\Dev.items.folder\ISOM3270_Startup`）依序執行：

```powershell
# Step 1: 把所有 Claude Code 的工作成果加入暫存區（包含新文件）
git add -A

# Step 2: 提交所有本地的變更
git commit -m "feat: Phase 2 - MiroFish swarm, EdgeBuild UI, open-source real integration"

# Step 3: 從 GitHub 拉取 Manus 的更新（.gitignore、archive、Prompts 等）
# 使用 --no-rebase 避免衝突
git pull origin main --no-rebase

# Step 4: 如果 Step 3 彈出 Vim 編輯器，輸入 :wq 後按 Enter 儲存離開
# 如果彈出 VS Code 編輯器，直接儲存關閉即可

# Step 5: 推送到 GitHub
git push origin main
```

### 如果 Step 3 出現 Merge 衝突

只有以下文件可能有衝突（因為兩端都修改了）：
- `.gitignore`：保留 GitHub 版本（Manus 版本更完整）
  ```powershell
  git checkout --theirs .gitignore
  git add .gitignore
  git merge --continue
  ```

---

## 五、同步完成後的驗證

執行完上述指令後，請執行以下指令確認同步成功：

```powershell
git status
# 應該顯示：nothing to commit, working tree clean

git log --oneline -5
# 應該看到你的 commit 在最上面
```

---

## 六、接下來的任務分工

### William 需要做的事
1. 執行上方的 4 個 git 指令，完成同步。
2. 在 `.env` 檔案中填入 `ZEP_API_KEY` 和 `LLM_API_KEY`（GLM-4）。
3. 執行 `cd agent && pip install -r requirements.txt` 安裝新依賴。
4. 在 Demo 前測試 `python agent/pm_arb_agent.py --dry-run` 確認 Swarm 功能正常。

### Manus 可以做的事
- 幫你 QA 審查 Claude Code 的代碼品質（push 成功後）。
- 幫你撰寫期末報告（基於 `PolyAlpha Protocol — Complete Revised Project.md`）。
- 幫你優化 Pitch Deck（基於上傳的 PPTX）。
- 幫你部署前端到 Vercel（按照 `docs/Vercel_Deployment_Guide.md`）。

### Claude Code 需要做的事（你的下一個 Prompt）
- 把 `PolyAlpha_6_OpenSource_REAL_Integration_Prompt.md` 的內容貼給它，讓它真正實作 6 大開源整合（safety_gate、momentum_scorer、news_client 等）。
- 確保它每次完成後都執行 `git add -A && git push origin main`。
