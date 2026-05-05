# Claude Code Prompt: Open-Source Alpha Integration

> **William**: 請將以下整段內容複製，並貼入你本地 VS Code 的 Claude Code 終端機中執行。

```text
[ROLE & TASK]
You are an expert Web3/AI Tech Lead. My project is "PolyAlpha Protocol" (a Polymarket vault + rule-based AI agent + dashboard). 
I have collected over 19 open-source GitHub repositories and X (Twitter) threads about Polymarket trading bots, AI agents, and Web3 tools. 
I do NOT want to build from scratch. I want to extract profitable ideas, algorithms, and reusable code from these links and integrate them into my project.

[CONTEXT & MEMORY]
Project: PolyAlpha Protocol (ISOM3270 Final Project)
Working Directory: C:\Users\user\Desktop\Dev.items.folder\ISOM3270_Startup
Current State: Vault deployed on ChainLab Testnet, React Dashboard running, Python Agent running in Paper Trading Mode.
Goal: Transition to Dry-run mode (live API, no real money) by integrating proven open-source strategies (win rate > 55%, drawdown < 10%), integrating with runes_leo, BitPilot, and finding fast-resolution Polymarket arbitrage opportunities (>95% probability).

[PREREQUISITE CHECK]
Before starting, ensure you have the `web-access` and `read-github` skills installed. If not, tell me to install them first using the previous Infrastructure Q&A Guide.

[INPUT DATA]
Here is the list of links I collected:
1. https://polyainews.vercel.app/
2. https://github.com/Polymarket/polymarket-cli
3. https://github.com/mco-org/mco
4. https://x.com/mirrorzk/status/2023303202196570420
5. https://x.com/runes_leo/status/2026824251165258235
6. https://brief.day1global.xyz/
7. https://conway.tech/
8. https://x.com/giantcutie666/status/2024600883741544500
9. https://x.com/RohOnChain/status/2023781142663754049
10. https://x.com/Jackm4xx/status/2023708378628030921
11. https://github.com/openai/codex-plugin-cc
12. https://github.com/numman-ali/openskills
13. https://mirofish-demo.pages.dev/
14. https://x.com/bcherny/status/2038454336355999749
15. https://github.com/Blave-TW/blave-quant-skill
16. https://github.com/6551Team/daily-news
17. https://cryptoskills.dev/
18. https://x.com/hunterweb303/status/2042905007834673495
19. https://x.com/hunterweb303/status/2039301057038467275

[YOUR WORKFLOW]
Please execute the following steps ONE BY ONE. Do not rush.

STEP 1: BROWSE & ANALYZE
Use your web fetching/searching tools (`web-access`, `read-github`) to visit these links. For X (Twitter) links, extract the core trading strategy or tool mentioned. For GitHub links, read their README and core logic files.

STEP 2: FILTER & CATEGORIZE
Filter out the noise. Categorize the useful ones into:
A. Trading Strategies / Alpha (Profitable ideas we can code into our agent.py, specifically fast-resolution arb and runes_leo/BitPilot integrations)
B. Infrastructure / Tools (Code we can directly copy-paste, like Polymarket API wrappers)
C. Dashboard / UI Inspiration

STEP 3: GENERATE REPORT
Create a markdown file named `OpenSource_Integration_Plan.md` in my workspace. For each useful link, provide:
- Core Edge: What makes it profitable or useful?
- Reusable Code: Exactly which file or function we should copy.
- Integration Plan: How to fit it into PolyAlpha's existing `agent.py` or `PolyAlphaVault.sol`.

STEP 4: MEMORY STORAGE
If you have `claude-mem` installed, ensure this analysis is saved to your persistent memory so you can recall these strategies when we actually write the code later.

Start with STEP 1 now. Tell me which links you are analyzing first.
```
