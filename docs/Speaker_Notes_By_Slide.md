# PolyAlpha Protocol — Speaker Notes (Slide by Slide)

> **使用說明**：這份文件為你 16 頁的 Pitch Deck 提供了逐頁的「演講備註」。你可以把它印出來，或是放在演講者畫面上。當 Q&A 被問到特定頁面時，你可以立刻參考底部的「🔥 必備 Q&A」來回答。

---

## Slide 1: Cover (封面)
- **🎤 演講詞**：Good morning, Professor and everyone. I am William Yong. Today, I am thrilled to introduce PolyAlpha Protocol — the infrastructure layer for AI-driven prediction market finance.
- **💡 備註**：微笑，環視全場，展現自信。確保大家有看清楚 Vercel 的 Demo 網址。

---

## Slide 2: The Problem (問題痛點)
- **🎤 演講詞**：Prediction markets like Polymarket have exploded, reaching billions in volume. But they suffer from a massive structural problem: the "favorite-longshot bias." Retail investors consistently overprice low-probability events. However, capitalizing on this mispricing requires speed, data infrastructure, and capital that everyday users simply do not have.
- **📊 關鍵數據**：
  - $1.5B TAM (Total Addressable Market)
  - Favorite-Longshot Bias (熱門-冷門偏差)
- **🔥 必備 Q&A**：
  - **Q: 什麼是 Favorite-Longshot Bias？**
  - A: 這是一種行為金融學現象。散戶喜歡買「賠率高、機率低」的選項（像買彩券），導致冷門選項價格被高估；同時他們覺得熱門選項賺太少，導致熱門選項被低估。我們的 AI 就是專門套利這種定價錯誤。

---

## Slide 3: Market Size (市場規模)
- **🎤 演講詞**：This isn't a niche market. The Total Addressable Market for prediction markets is projected to hit $1.5 billion. Yet, institutional-grade tools remain locked behind proprietary black boxes.
- **📊 關鍵數據**：
  - TAM: $1.5B (Prediction Markets)
  - SAM: $300M (DeFi Yield Seekers)
  - SOM: $15M (PolyAlpha Target TVL)
- **🔥 必備 Q&A**：
  - **Q: 你們的 SOM ($15M) 怎麼估算的？**
  - A: 我們假設在 Phase 3 啟動後，能夠捕捉 Polymarket 總交易量約 1% 的流動性作為我們的 Vault TVL，這是一個保守且可達成的目標。

---

## Slide 4: The Solution (解決方案)
- **🎤 演講詞**：Enter PolyAlpha Protocol. We democratize quantitative arbitrage. By combining an ERC-4626 Vault, an autonomous AI engine, and DAO governance, we allow anyone to deposit USDC and earn yield from structural market inefficiencies.
- **💡 備註**：用手勢強調三個支柱：Vault (資產), AI Engine (大腦), DAO (治理)。

---

## Slide 5: How It Works (運作流程)
- **🎤 演講詞**：The workflow is simple. Investors deposit USDC into our smart contract vault. Our off-chain Python agent continuously scans Polymarket, filters sentiment using our integrated AI, and executes trades when the Kelly criterion confirms a positive expected value. Profits flow back to the vault.
- **🔥 必備 Q&A**：
  - **Q: 為什麼 AI 運算要在 Off-chain (鏈下) 進行？**
  - A: 預測市場的訂單簿更新頻率極高，且 AI 情緒分析需要呼叫外部 API。如果全部放在鏈上（On-chain），Gas Fee 會高到無法獲利，且交易延遲會導致錯失套利機會。

---

## Slide 6: Alpha Engine (AI 引擎架構)
- **🎤 演講詞**：Our Alpha Engine is the brain. It doesn't just guess. It uses a 4-layer signal stack, processing real-time order books and crypto news sentiment, ensuring we only trade when the mathematical edge is in our favor.
- **📊 關鍵數據**：4 層架構 (Data Ingestion, Signal Generation, Risk Filter, Execution)
- **🔥 必備 Q&A**：
  - **Q: 你的 AI 引擎具體用什麼策略？**
  - A: 我們目前實作了兩種：一是 Yes/No 價格加總小於 $1.00 的無風險套利；二是基於三因子動能模型（ROC, RSI, MACD）與新聞情緒的趨勢跟蹤策略。

---

## Slide 7: Live Dashboard Demo (前端展示)
- **🎤 演講詞**：And this is our live dashboard. Built with React and deployed on Vercel, it provides absolute transparency. Users can track every AI signal, view the vault's TVL, and monitor backtest results in real-time.
- **💡 備註**：如果你有準備 45 秒影片，可以在這裡播放。如果沒有，請引導教授看簡報上的截圖與網址。

---

## Slide 8: Technical Architecture (技術架構)
- **🎤 演講詞**：Technically, we deployed 6 core smart contracts on the ChainLab Testnet, written in Solidity 0.8.25. Our architecture strictly separates the on-chain asset management from the off-chain high-frequency computation.
- **📊 關鍵數據**：
  - Solidity 0.8.25, EVM Cancun, OpenZeppelin v5
  - ChainLab Testnet (chainId: 31337)
- **🔥 必備 Q&A**：
  - **Q: 為什麼選擇 ERC-4626 標準？**
  - A: ERC-4626 是代幣化金庫（Tokenized Vaults）的黃金標準。它標準化了存款和份額（Shares）鑄造的邏輯，讓我們的 Vault 未來可以輕易地與其他 DeFi 協議（如 Aave 或 Uniswap）整合。

---

## Slide 9: Security Model (安全模型)
- **🎤 演講詞**：Security is paramount. Before any trade executes, it must pass our 6-step BitPilot Safety Chain — including daily trade caps, position limits, and a circuit breaker to prevent catastrophic drawdowns.
- **📊 關鍵數據**：
  - 每日最多 5 筆交易
  - 單筆交易不超過 TVL 10%
  - 最大回撤 (Drawdown) 達 15% 觸發熔斷 (Circuit Breaker)

---

## Slide 10: Tokenomics (代幣經濟學)
- **🎤 演講詞**：To align incentives, we introduced the PALPHA token. It features a buyback-and-burn mechanism funded by 10% of trading profits, ensuring deflationary pressure as the protocol grows.
- **🔥 必備 Q&A**：
  - **Q: PALPHA 代幣的價值支撐是什麼？**
  - A: 第一是治理權（決定哪些 AI 策略可以上線）；第二是通縮機制，我們從 20% 的 Performance Fee 中抽出 10% 在市場上回購並銷毀 PALPHA，創造持續的買盤。

---

## Slide 11: Open-Source Integration (開源整合優勢)
- **🎤 演講詞**：What makes us unique? We didn't reinvent the wheel. We integrated 6 proven open-source projects — from Polymarket's CLOB API to MiroFish's multi-agent swarm AI — achieving 10x faster development and institutional-grade quality.
- **🔥 必備 Q&A**：
  - **Q: 你們怎麼使用 MiroFish Swarm AI？**
  - A: 我們不依賴單一的 GPT-4 prompt，因為容易有幻覺。我們用 MiroFish 模擬 5 種不同人格（例如反向投資者、趨勢跟蹤者），讓他們根據新聞獨立投票。只有當 Swarm 達成強烈共識時，我們才執行交易。

---

## Slide 12: Competitive Landscape (競爭分析)
- **🎤 演講詞**：Compared to centralized SaaS platforms or traditional quant funds, PolyAlpha is the *only* platform combining on-chain transparency, DAO governance, and open-source AI arbitrage.
- **💡 備註**：強調「Transparency (透明度)」是 Web3 專案打敗傳統金融的最大武器。

---

## Slide 13: Strategy Validation (策略回測驗證)
- **🎤 演講詞**：The math works. Our paper trading simulation over 2 years of data yielded a 62.3% win rate and a Sharpe ratio of 2.1, proving the strategy's robustness.
- **📊 關鍵數據**：
  - Win Rate: 62.3%
  - Sharpe Ratio: 2.1
  - Max Drawdown: 11.2%
- **🔥 必備 Q&A**：
  - **Q: 你們的 PnL (損益) 是怎麼計算的？**
  - A: 我們嚴格採用 Cash-Flow (現金流) 模型，也就是真實的 Payout 減去 Cost，而不是簡單計算賠率差。這包含了手續費與滑點的估算，更貼近真實市場。

---

## Slide 14: Business Model (商業模式)
- **🎤 演講詞**：Our business model is a sustainable 2/20 hedge fund structure. 2% management fee, 20% performance fee. At our Phase 3 target of $10 million TVL, this generates over half a million in annual revenue.
- **📊 關鍵數據**：
  - 2% Management Fee (管理費)
  - 20% Performance Fee (績效費)
  - $10M TVL = $574K Annual Revenue
- **🔥 必備 Q&A**：
  - **Q: 如果 AI 虧錢了，你們還收費嗎？**
  - A: 20% 的 Performance Fee 設有 High-Water Mark (高水位線)，只有在淨值創歷史新高時才收費。2% 的 Management Fee 則是維持伺服器與 API 運作的基礎成本。

---

## Slide 15: Roadmap (發展路線)
- **🎤 演講詞**：We have completed Phase 1 foundation. We are currently in Phase 2 integrating Swarm Intelligence, and we are on track for a mainnet launch by Q4 2026.
- **💡 備註**：展現專案是有計畫性、可執行的，而不只是個學校作業。

---

## Slide 16: Conclusion & CTA (結語)
- **🎤 演講詞**：PolyAlpha Protocol is not just a concept. It is a fully deployed, transparent, and scalable infrastructure for the future of decentralized finance. Thank you. I am now open to questions.
- **💡 備註**：停留在此頁，讓大家掃描 QR Code 或抄下 GitHub 網址。準備好迎接 Q&A。
