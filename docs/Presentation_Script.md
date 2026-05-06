# PolyAlpha Protocol — Final Presentation Script

> **Presenter**: William Yong
> **Course**: ISOM3270 Blockchain Programming in Business Applications
> **Time Limit**: 7 minutes presentation + 3 minutes Q&A

---

## Option 1: Full Speech (700 words + Q&A)
*Best if you want to verbally explain the entire architecture without a video demo.*

**[Slide 1: Cover]**
*(Stand confidently in the center. Smile. Pause for 2 seconds before speaking.)*
"Good morning, Professor and everyone. I am William Yong. Today, I am thrilled to introduce PolyAlpha Protocol — the infrastructure layer for AI-driven prediction market finance."

**[Slide 2: The Problem]**
*(Step slightly to the left, gesture to the screen with an open hand.)*
"Prediction markets like Polymarket have exploded, reaching billions in volume. But they suffer from a massive structural problem: the 'favorite-longshot bias.' Retail investors consistently overprice low-probability events. However, capitalizing on this mispricing requires speed, data infrastructure, and capital that everyday users simply do not have."

**[Slide 3: Market Size]**
*(Point to the chart.)*
"This isn't a niche market. The Total Addressable Market for prediction markets is projected to hit $1.5 billion. Yet, institutional-grade tools remain locked behind proprietary black boxes."

**[Slide 4: The Solution]**
*(Bring hands together, speak with emphasis.)*
"Enter PolyAlpha Protocol. We democratize quantitative arbitrage. By combining an ERC-4626 Vault, an autonomous AI engine, and DAO governance, we allow anyone to deposit USDC and earn yield from structural market inefficiencies."

**[Slide 5: How It Works]**
*(Use hand gestures to trace a flow from left to right.)*
"The workflow is simple. Investors deposit USDC into our smart contract vault. Our off-chain Python agent continuously scans Polymarket, filters sentiment using our integrated AI, and executes trades when the Kelly criterion confirms a positive expected value. Profits flow back to the vault."

**[Slide 6: Alpha Engine]**
*(Pace slightly, maintain eye contact with the audience.)*
"Our Alpha Engine is the brain. It doesn't just guess. It uses a 4-layer signal stack, processing real-time order books and crypto news sentiment, ensuring we only trade when the mathematical edge is in our favor."

**[Slide 7: Live Dashboard]**
*(Gesture broadly to the UI screenshots.)*
"And this is our live dashboard. Built with React and deployed on Vercel, it provides absolute transparency. Users can track every AI signal, view the vault's TVL, and monitor backtest results in real-time."

**[Slide 8: Technical Architecture]**
*(Briefly point to the smart contract table.)*
"Technically, we deployed 6 core smart contracts on the ChainLab Testnet, written in Solidity 0.8.25. Our architecture strictly separates the on-chain asset management from the off-chain high-frequency computation."

**[Slide 9: Security Model]**
*(Adopt a serious, reassuring tone.)*
"Security is paramount. Before any trade executes, it must pass our 6-step BitPilot Safety Chain — including daily trade caps, position limits, and a circuit breaker to prevent catastrophic drawdowns."

**[Slide 10: Tokenomics]**
*(Smile, use an upward hand gesture.)*
"To align incentives, we introduced the PALPHA token. It features a buyback-and-burn mechanism funded by 10% of trading profits, ensuring deflationary pressure as the protocol grows."

**[Slide 11: Open-Source Integration]**
*(Speak with pride.)*
"What makes us unique? We didn't reinvent the wheel. We integrated 6 proven open-source projects — from Polymarket's CLOB API to MiroFish's multi-agent swarm AI — achieving 10x faster development and institutional-grade quality."

**[Slide 12: Competitive Landscape]**
*(Point to the comparison table.)*
"Compared to centralized SaaS platforms or traditional quant funds, PolyAlpha is the *only* platform combining on-chain transparency, DAO governance, and open-source AI arbitrage."

**[Slide 13: Strategy Validation]**
*(Gesture to the PnL chart.)*
"The math works. Our paper trading simulation over 2 years of data yielded a 62.3% win rate and a Sharpe ratio of 2.1, proving the strategy's robustness."

**[Slide 14: Business Model]**
*(Emphasize the numbers.)*
"Our business model is a sustainable 2/20 hedge fund structure. 2% management fee, 20% performance fee. At our Phase 3 target of $10 million TVL, this generates over half a million in annual revenue."

**[Slide 15: Roadmap]**
*(Pace back to the center.)*
"We have completed Phase 1 foundation. We are currently in Phase 2 integrating Swarm Intelligence, and we are on track for a mainnet launch by Q4 2025."

**[Slide 16: Conclusion]**
*(Stand still, project confidence, make eye contact with the Professor.)*
"PolyAlpha Protocol is not just a concept. It is a fully deployed, transparent, and scalable infrastructure for the future of decentralized finance. Thank you. I am now open to questions."

---

## Option 2: Demo-Focused Speech (600 words + 45s Video Demo + Q&A)
*Best if you have a screen recording of the Vercel Dashboard and Python Agent running.*

**[Slide 1-4: Intro & Problem]** (Same as Option 1, but slightly faster pace. ~1.5 mins)
*(Standard introduction, highlight the favorite-longshot bias and the TAM.)*

**[Slide 5: How It Works & Video Demo Transition]**
*(Stop pacing, turn towards the screen.)*
"Instead of just explaining the architecture, I want to show you exactly how PolyAlpha works in practice. Let's look at the live demo."

**[Start 45s Video Demo]**
*(Stand to the side, narrate over the video. Point to the screen when mentioning specific features.)*
*(0:00 - 0:15)* "Here is our live React dashboard deployed on Vercel. As an investor, I connect my wallet and deposit USDC into the ERC-4626 Vault. The transaction is instantly recorded on the ChainLab Testnet."
*(0:15 - 0:30)* "Meanwhile, in the background, our Python Agent is running. You can see the terminal output here: it's pulling real-time order book data, analyzing news sentiment, and running the 6-step safety check."
*(0:30 - 0:45)* "Once a profitable arbitrage opportunity is found, the agent logs the signal on-chain, and the dashboard updates immediately. Complete transparency, zero black boxes."

**[Slide 8-10: Tech & Security]**
*(Resume center stage, speak with authority.)*
"As you saw, the execution is seamless. This is powered by our 6 Solidity smart contracts and an off-chain computation layer. We prioritize security with a strict circuit breaker and align user incentives through the PALPHA token's buyback-and-burn model."

**[Slide 11-14: Open Source, Validation & Business Model]**
*(Use quick, sharp gestures to emphasize key metrics.)*
"Our edge comes from integrating 6 proven open-source projects, including MiroFish's Swarm AI. Backtesting proves a 62.3% win rate. Our revenue model is a standard 2/20 structure, ensuring sustainable cash flow from day one."

**[Slide 16: Conclusion]**
*(Smile, project confidence.)*
"PolyAlpha Protocol brings institutional quant strategies to decentralized markets. Thank you. I'm happy to take your questions."

---

## Potential Q&A Questions & Suggested Answers

**Q1 (Professor): Why use an off-chain Python agent instead of doing everything on-chain?**
**Answer**: "Great question. High-frequency data processing, like fetching Polymarket order books and running AI sentiment analysis, is computationally too expensive and slow for Ethereum or Polygon. By keeping the heavy lifting off-chain in Python and only logging the final trade decisions and asset management on-chain via our ERC-4626 vault, we achieve the perfect balance of speed and transparency."

**Q2: How do you prevent the AI agent from draining the vault if it makes a mistake?**
**Answer**: "We implemented a 6-step BitPilot Safety Chain in our Python agent. It includes a daily trade cap (maximum 5 trades per day), a position size limit (never risking more than 10% of TVL per trade), and a hard circuit breaker that halts all trading if the maximum drawdown exceeds 15%. The smart contract also has emergency pause functions."

**Q3: You mentioned the 'favorite-longshot bias'. How exactly does your agent exploit this?**
**Answer**: "Retail traders tend to overvalue low-probability events (longshots) and undervalue high-probability events (favorites). Our agent specifically targets markets where the 'Yes' and 'No' shares add up to less than $1.00, or where the implied probability significantly deviates from historical baselines. We use the Empirical Kelly criterion to size our bets dynamically based on our historical win rate, maximizing compound growth."

**Q4: Why did you integrate MiroFish Swarm AI instead of just using a single GPT-4 prompt?**
**Answer**: "A single LLM prompt is highly susceptible to hallucination and bias. MiroFish allows us to simulate 5 distinct AI personas—ranging from contrarian to trend-following. They independently analyze the market data and vote. We only execute a trade if there is a strong swarm consensus. This multi-agent approach significantly reduces false positives."
