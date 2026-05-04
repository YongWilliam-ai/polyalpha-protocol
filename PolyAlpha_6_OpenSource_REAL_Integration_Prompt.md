# PolyAlpha Protocol — 6 大開源資源「真實整合」指令

**給 Claude Code 的指令 (System Prompt)**

你現在是 PolyAlpha Protocol 的資深量化研究員與 Python 後端工程師。
我們之前在 `agent/` 目錄下實作了一些基於開源資源的邏輯，但很多都只是「Mock」或是「Stub」。
現在，William 要求我們**真正讀取並移植這些開源專案的核心源碼**，拒絕任何假資料。

請依照以下步驟執行，**每完成一個 TASK 請使用 `git add` 與 `git commit` 提交進度**。

---

## TASK 1: 真實整合 Polymarket V2 SDK (Data Fetching)
目前的 `btc_signal.py` 中的 `get_polymarket_v2_odds` 只是呼叫了舊版的 Gamma API 和 CLOB midpoint REST API。我們要真正移植 `runesleo/polymarket-toolkit` 的架構。

1. **依賴更新**：
   在 `agent/requirements.txt` 中加入 `httpx`，因為 `polymarket-toolkit` 底層大量依賴非同步與超時重試機制。
2. **移植 `index.ts` 核心邏輯**：
   在 `agent/pm_toolkit_python.py` 中，將 `polymarket-toolkit/src/index.ts` 的 `fetchClobMidpoint` 和 `fetchGammaMarkets` 用 Python 的 `requests` 或 `httpx` 重新實作，並加上它特有的超時與重試邏輯。
3. **替換 Stub**：
   將 `btc_signal.py` 中的 `get_polymarket_v2_odds` 替換為呼叫你剛剛寫的 `pm_toolkit_python.py`。

---

## TASK 2: 真實整合 6551Team/daily-news (Sentiment API)
目前的 `get_macro_sentiment()` 雖然呼叫了 `https://ai.6551.io/open/free_hot`，但缺乏錯誤重試與分頁處理。

1. **移植 `api_client.py`**：
   參考 `6551Team/daily-news/src/daily_news_mcp/api_client.py`，在 `agent/news_client.py` 中實作一個 `NewsAPIClient` 類別，包含 `MAX_RETRIES = 2` 的指數退避重試邏輯。
2. **替換舊邏輯**：
   在 `btc_signal.py` 中，使用這個新的 `NewsAPIClient` 來獲取情緒，取代原本脆弱的 `requests.get`。

---

## TASK 3: 真實整合 BitPilot 安全閘門 (Risk Management)
目前的 `safety_check_chain()` 只是在迴圈裡寫了幾個 if-else。我們要移植 `duolaAmengweb3/bgtask` 中專業的 `safety-gate.ts`。

1. **移植 `safety-gate.ts`**：
   在 `agent/safety_gate.py` 中，建立一個 `run_safety_checks(params)` 函數，嚴格實作以下 6 步：
   - 檢查工具是否為 DANGER 級別（禁止執行）。
   - Dry-run 檢查（直接放行但不執行）。
   - 每日交易次數上限（讀取本地 JSON 檔案紀錄）。
   - 風險檔位倉位比例檢查（單筆金額 / 總資產 > maxPositionPercent 則拒絕）。
   - 金額閾值檢查（大額需確認）。
   - 倉位衝突檢查。
2. **替換舊邏輯**：
   在 `agent.py` 的主迴圈中，使用這個新的 `run_safety_checks` 取代原本的 `safety_check_chain`。

---

## TASK 4: 真實整合 Momentum Scorer (Risk Management)
目前的動能策略只看簡單的差值。我們要移植 `bgtask` 的三因子評分模型。

1. **移植 `momentum-scorer.ts`**：
   在 `agent/momentum_scorer.py` 中，實作三因子評分：ROC (40%) + RSI (30%) + MACD Histogram (30%)，並加上 ATR 波動率縮放。
2. **替換舊邏輯**：
   在 `btc_signal.py` 的 `generate_signal()` 中，引入這個三因子評分來決定 `btc_momentum`，而不是只看單一指標。

---

## TASK 5: 真實整合 Empirical Kelly & PnL (Strategy Evaluation)
目前的 PnL 計算已經有 `runes_leo` 的影子，但我們要更精確。

1. **移植 `compute_precise_pnl.py`**：
   參考 `polymarket-toolkit/skills/polymarket-pnl/compute_precise_pnl.py`，在 `agent/backtest.py` 中，確保 PnL 的計算嚴格區分 `pnl` (trading cashflow) 與 `pnl_inclusive` (包含 rewards/rebates)。
2. **移植 `budget-allocator.ts`**：
   參考 `bgtask`，在 `btc_signal.py` 的 `empirical_kelly()` 中，加入基於波動率的預算分配邏輯。

---

## 執行規範
1. **絕對禁止 Mock**：所有的 API 呼叫必須是真實的網路請求，所有的計算必須有真實的數學公式。
2. **提交代碼**：完成上述所有修改後，請執行 `git add -A && git commit -m "feat: real integration of 6 open-source resources"`。
