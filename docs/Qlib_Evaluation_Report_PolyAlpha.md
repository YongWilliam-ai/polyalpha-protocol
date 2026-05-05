# Microsoft Qlib 評估報告：個人使用適用性與 PolyAlpha 專案整合指南

**作者**：William (資深產品經理視角)
**專案**：PolyAlpha Protocol
**日期**：2026 年 4 月 30 日

---

## 1. 執行摘要 (Executive Summary)

本報告以資深產品經理（PM）的視角，針對微軟亞洲研究院（MSRA）開源的量化投資平台 **Microsoft Qlib** 進行全面評估。評估的核心目標在於釐清 Qlib 對於個人開發者（特別是學生或獨立研究者）的適用性，並探討其與 PolyAlpha Protocol 的整合潛力。

**核心結論**：Qlib 是一個強大的「AI 量化研究基礎設施」，而非「開箱即用的交易機器人」。對於目前的 PolyAlpha 專案（MVP 階段），**不建議在短期內整合 Qlib**。Qlib 應被定位為 PolyAlpha 未來（Phase 2/3）的**離線研究引擎（Research Engine）**，用於驗證預測市場的定價偏差與訓練更複雜的預測模型。

---

## 2. Microsoft Qlib 核心定位

### 2.1 Qlib 是什麼？不是什麼？

| 比較維度 | Backtrader | VnPy | Microsoft Qlib |
|---|---|---|---|
| 核心定位 | 事件驅動的回測引擎 | 全端量化交易平台 | AI 導向的量化研究與機器學習平台 |
| 主要強項 | 語法優雅，適合學習傳統技術指標回測 | 實盤交易介面完善（特別是中國市場） | 內建 40+ 頂級機器學習模型與因子庫 |
| 機器學習支援 | 極弱（需自行串接） | 弱（偏向傳統 CTA 策略） | 極強（原生支援 LightGBM, LSTM, Transformer 等） |
| 實盤交易能力 | 弱（已停止維護） | 極強（無縫從回測切換至實盤） | 弱（需自行開發經紀商 API 串接） |

Qlib 的架構包含資料伺服器（DataServer）、學習框架（Learning Framework）與工作流（Workflow）。其最大的亮點在於提供了標準化的 Alpha158/Alpha360 因子庫，以及近期整合的 **RD-Agent**（基於 LLM 的自動化研發代理），能自動進行因子挖掘與模型優化。

### 2.2 個人使用適用性與學習曲線

Qlib 對個人開發者的主要挑戰：

1. **極高的技術門檻**：使用者不僅需要扎實的 Python 能力，還必須同時具備機器學習（PyTorch, LightGBM）與量化金融（多因子模型）的背景知識。
2. **生產環境落差**：Qlib 是研究工具，並非生產級的交易基礎設施。它沒有內建的券商 API，也沒有即時串流資料處理能力。
3. **資料準備繁瑣**：若要應用於 Polymarket 預測市場，使用者必須自行編寫腳本，將資料轉換為 Qlib 特定的二進位格式。

---

## 3. 與 PolyAlpha Protocol 現況的適配度評估

### 3.1 短期計畫（MVP 階段）：不建議整合 Qlib

在目前的 MVP 階段，強烈建議**不要**安裝或整合 Qlib。原因如下：

- **過度工程化（Overengineering）**：目前只需要一個能讀取 Polymarket JSON API 並計算簡單 Edge 的 Python 腳本。引入 Qlib 會破壞 SOP 中「保持 AI 代理極度簡單」的原則。
- **資產類別不匹配**：Qlib 預設針對股票（連續價格）設計。Polymarket 是二元期權（Binary Options），價格介於 0 到 1 之間，代表機率。
- **偏離專案核心**：教授的評分重點在於「智慧合約金庫的透明度」與「代幣經濟學（$PALPHA）」。

### 3.2 未來計畫（Phase 2/3）：將 Qlib 作為離線研究引擎

**混合架構（Hybrid Approach）**：

```
[ 離線研究層 (Offline Research) ]
工具：Microsoft Qlib + RD-Agent
任務：輸入 Becker 400M 歷史資料，訓練預測模型，驗證 Favorite-Longshot Bias，產出靜態規則或模型權重。
↓
[ 執行與決策層 (Live Execution) ]
工具：目前的 Python Agent (signal_engine.py)
任務：讀取 Qlib 產出的規則/模型，結合即時 Polymarket API，計算 Kelly Size，發送交易信號。
↓
[ 鏈上結算層 (On-chain Vault) ]
工具：PolyAlphaVault.sol (Polygon)
任務：記錄 logPosition()，管理資金，執行 DAO 治理。
```

---

## 4. 具體行動建議與路線圖

| 步驟 | 時間點 | 行動 |
|---|---|---|
| 步驟一 | 現在至期末報告 | 放棄 Qlib；在期末報告中將其寫入「Phase 2 未來展望」 |
| 步驟二 | 暑期或專案結束後 | 建立 Polymarket 資料集，清洗為 Qlib 支援的格式 |
| 步驟三 | Phase 2 | 安裝 Qlib，進行因子挖掘，訓練 LightGBM/LSTM 模型 |
| 步驟四 | Phase 3 | 引入 RD-Agent，讓 LLM 自動生成新的交易因子（Alpha） |

---

## 5. 總結

Microsoft Qlib 是一個頂級的學術與研究工具，能夠極大地提升量化策略的研發效率。然而，它不是一個實盤交易框架。

對於 PolyAlpha 而言，目前的痛點在於「證明系統能運作（Prove the loop works）」，因此應堅守輕量級的 Python 腳本。未來，當需要從預測市場中榨取真實利潤時，將 Qlib 作為離線的策略大腦，定期輸出交易規則給輕量級的執行 Agent，將是兼顧研發深度與系統穩定性的最佳架構。

---

## 參考文獻

- [1] Tianpan.co. (2026). Microsoft Qlib: A panoramic assessment for quantitative trading infrastructure.
- [2] DEV Community. (2026). Backtrader vs VnPy vs Qlib: A Deep Comparison of Python Quant Backtesting Frameworks.
- [3] Microsoft Research. (2025). R&D-Agent-Quant: A Multi-Agent Framework for Data-Centric Factors and Model Joint Optimization. https://github.com/microsoft/qlib
