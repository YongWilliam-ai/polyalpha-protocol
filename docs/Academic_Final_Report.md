# PolyAlpha Protocol: A DAO-Governed, AI-Driven Market-Making Vault

**Course:** ISOM3270 Blockchain Programming in Business Applications  
**Student:** William Yong  
**Date:** May 8, 2026  

## I. Executive Summary & Problem Statement

### Project Introduction
PolyAlpha Protocol is a decentralized finance (DeFi) application that combines an ERC-4626 smart contract vault, a rule-based AI trading agent, and a DAO governance model. The protocol is designed to capture yield from decentralized prediction markets like Polymarket by systematically exploiting structural pricing inefficiencies. It bridges the gap between sophisticated quantitative arbitrage and decentralized finance, offering an institutional-grade yield infrastructure accessible to retail investors.

### Problem Definition & Pain Point
Prediction markets suffer from the well-documented "favorite-longshot bias," where retail participants consistently overprice low-probability events (longshots) and underprice high-probability events (favorites) [1]. Capitalizing on this bias requires high-frequency data infrastructure, complex quantitative models, and significant capital, creating an impossible barrier to entry for everyday investors. Retail users lack the speed to react to order book changes in milliseconds, the data infrastructure for real-time sentiment feeds, and the capital to overcome gas fees and slippage.

### Limitations of Current Solutions
Current solutions fall into two extremes:
1. **Centralized SaaS Platforms:** Lack on-chain transparency, require trusting a centralized entity, and have no DAO governance [2].
2. **Traditional Quant Funds:** Operate as proprietary black boxes, completely inaccessible to retail investors, often requiring $1,000,000+ minimum deposits and imposing multi-year lock-up periods.

### Proposed Solution & Innovation
PolyAlpha democratizes quantitative arbitrage by allowing anyone to deposit USDC into an on-chain vault with a minimum deposit of just $10. An off-chain AI agent, integrated with six proven open-source projects, autonomously executes trades based on the Empirical Kelly criterion. All trade signals are logged immutably on-chain, providing 100% transparency. The protocol is governed by the PALPHA token, aligning incentives through a deflationary buyback-and-burn mechanism.

## II. Business & Market Analysis

### Target Market & Size
The global prediction market volume experienced a 302% year-over-year growth, reaching $63.5 billion in 2025, with Polymarket alone accounting for $220 billion in trading volume [3]. The Total Addressable Market (TAM) is $63.5 billion, while the Serviceable Available Market (SAM) for automated arbitrage is estimated at $6.3 billion. PolyAlpha targets a Serviceable Obtainable Market (SOM) of $15 million for its Phase 3 TVL goal.

### Value Proposition
PolyAlpha offers a unique value proposition: **Institutional-grade quant strategies with Web3 transparency.** Users gain access to advanced AI arbitrage without needing technical expertise, while retaining full visibility into the vault's operations via a React-based dashboard. The protocol operates on a non-custodial basis, ensuring users retain control of their assets.

### Competitive Analysis & Advantage
Compared to competitors like Polymarket (direct trading), Augur, Numerai, and Yearn Finance, PolyAlpha is the *only* platform combining prediction market focus, automated AI execution, on-chain transparency, and a DAO governance token [4]. 

A core competitive advantage is the integration of six battle-tested open-source protocols:
1. **MiroFish Swarm AI:** A multi-agent system where 5 AI personas vote independently on trades, ensuring robust consensus.
2. **polymarket-toolkit:** Provides real-time order book data and cash-flow PnL calculation.
3. **daily-news (6551Team):** Supplies real-time news sentiment scoring to filter trades.
4. **BitPilot Safety Chain:** A 6-step safety gate including daily trade caps and circuit breakers.
5. **Microsoft Qlib:** A backtesting framework used to validate the strategy, achieving a 2.1 Sharpe ratio.
6. **CAMEL-OASIS:** An agent memory framework ensuring persona persistence across trading sessions.

### Go-to-Market (GTM) Strategy
Our GTM strategy focuses on building trust through transparency. We will open-source our backtesting data, which demonstrates a 62.3% win rate and a 2.1 Sharpe ratio over 24 months of historical data. A community-driven DAO will incentivize early adopters with PALPHA token rewards, solving the cold-start problem and bootstrapping initial liquidity.

## III. Technical Architecture

### System Overview
The system is divided into three modular layers:
1. **On-Chain Layer:** 6 core Solidity (v0.8.25) contracts deployed on the Polygon Amoy Testnet (chainId: 80002).
2. **Off-Chain Agent Layer:** A Python-based engine handling data ingestion, sentiment analysis, swarm validation, and trade execution.
3. **Frontend Layer:** A React + TailwindCSS application deployed on Vercel for user interaction and monitoring.

### Data Design (On-chain & Off-chain)
- **Off-Chain:** The Python agent fetches real-time CLOB data from Polymarket, sentiment scores from the daily-news API, and utilizes the MiroFish Swarm AI for signal validation.
- **On-Chain:** Only the final trade decisions, asset management (deposits/withdrawals), and performance metrics are logged on-chain. This minimizes gas costs while maintaining full auditability. Every oracle input is SHA-256 hashed on-chain to ensure tamper resistance.

### Smart Contract Functions
- `PolyAlphaVault.sol`: An ERC-4626 compliant vault managing USDC deposits and share minting.
- `PALPHAToken.sol`: The native ERC-20 governance and utility token.
- `PALPHABuybackBurn.sol`: Automatically allocates a portion of performance fees to buy back and burn PALPHA tokens.
- `PALPHAGovernance.sol`: Facilitates DAO voting on protocol parameters.
- `PALPHAStaking.sol`: Manages yield distribution for staked tokens.
- `PALPHAOracle.sol`: Handles Chainlink-compatible price feeds.

### Security Considerations
Security is enforced via the hardcoded 6-layer BitPilot Safety Chain:
1. **Blacklist Check:** Blocks dangerous or illiquid markets.
2. **Position Limit:** Maximum 10% of TVL per single trade.
3. **Daily Cap:** Maximum 20 trades per day.
4. **Size Limit:** Maximum 0.05% of TVL per trade to prevent slippage.
5. **Conflict Check:** Prevents opposing positions in the same market.
6. **Circuit Breaker:** Halts all trading if the maximum drawdown exceeds 20%. This is hardcoded in the smart contract and cannot be overridden by an admin.

### Test Results & Analysis
Backtesting on 24 months of historical Polymarket data (Jan 2024 to May 2026) using the Microsoft Qlib framework yielded a 62.3% win rate, a Sharpe ratio of 2.1, and a maximum drawdown of -18.3% [5]. The strategy utilizes Quarter-Kelly sizing to optimize growth while strictly controlling risk.

## IV. Business Model & Tokenomics Design

### Revenue Streams
PolyAlpha operates on a sustainable 2/20 hedge fund structure, mirroring top traditional funds but with full on-chain transparency and no lock-up periods:
- **2% Annual Management Fee** on total value locked (TVL).
- **20% Performance Fee** on profits generated by the AI agent.

### Financial Projection and Analysis
Assuming a Phase 3 target of $10M TVL and an 18.7% annual return, the protocol projects $200,000 in management fees and $374,000 in performance fees, totaling $574,000 in annual revenue.

### Token Utility & Economic Model
The PALPHA token (Total Supply: 100,000,000) is a deflationary governance token aligned with protocol performance. It offers six core utilities:
1. **Governance:** Voting on AI rules, fee rates, and treasury allocation.
2. **Fee Discounts:** Holding PALPHA reduces performance fees.
3. **Early Access:** Required for vault deposits during the bootstrap phase.
4. **Staking Yield:** Stakers earn 8-15% APY plus a share of protocol revenue.
5. **Protocol Payments:** Fees can be paid in PALPHA.
6. **Deflationary Burn:** 20% of performance fees are used to buy back and burn PALPHA, decreasing supply and increasing value.

## V. Conclusion
PolyAlpha Protocol successfully bridges the gap between sophisticated AI arbitrage and decentralized finance. By integrating six proven open-source technologies and maintaining strict on-chain transparency, it provides a scalable, secure, and profitable infrastructure layer for prediction market finance. The successful deployment of Phase 1 and the ongoing Phase 2 integrations position PolyAlpha for a strong mainnet launch, transforming prediction market alpha into a trustless, community-owned asset.

## References
[1] Vaughan Williams, L. (1999). Information efficiency in betting markets: A survey. *Bulletin of Economic Research*, 51(1), 1-30.  
[2] EdgeBuild Documentation. (2025). *Platform Architecture and Centralization Risks*.  
[3] Polymarket Analytics & CoinGecko Annual Report. (2025). *Global Prediction Market Volume*.  
[4] PolyAlpha Competitive Landscape Analysis. (2026). *Internal Project Data*.  
[5] PolyAlpha Backtest Report. (2026). *Walk-forward validation using Microsoft Qlib Alpha158 factor library*.
