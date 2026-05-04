# PolyAlpha_Daily_Todo_Sprint

## Purpose

This file is the **execution board** for PolyAlpha.
It is not a strategy memo.
It is the day-by-day operating checklist that turns the project into a shipped prototype.

Core rule:
- **Vault first**
- **AI second**
- **Dashboard third**
- If anything breaks, protect the vault scope first

---

## Non-Negotiable Build Order

This project follows the sequence your professor effectively approved:
1. Build the vault contract first.
2. Keep the AI agent rule-based with only 1–2 clear rules.
3. Use Polymarket read API / SDK first, not full live execution.
4. Build the dashboard only after the core pipeline works.

Project passing logic:
- Minimum passing core = working vault + deposit/withdraw + event logging
- Strong project = vault + rule-based agent + logged signals
- Excellent demo = vault + agent + dashboard + simple backtest view

---

## Daily Operating Rules

Use these rules every day:
- Start with one **ship target** only.
- Work in 90-minute blocks.
- If blocked for over 30 minutes, simplify scope instead of researching endlessly.
- End each work session by updating Notion / markdown progress log.
- Never open a new branch of work before the current one has a visible artifact.

Definition of a valid work session:
- A compiled contract
- A passing script
- A saved screenshot
- A deployed testnet contract
- A pushed commit
- A markdown note with concrete decisions

---

## Master Sprint

## Sprint A — Vault Foundation

### Day 1

**Goal:** Get the vault skeleton compiling.

Tasks:
- Create `PolyAlphaVault.sol` in Remix.
- Base it on ERC-4626 structure.
- Include deposit / withdraw flow.
- Add `Ownable` and `ReentrancyGuard`.
- Add `logPosition()` event for AI decisions.
- Compile successfully.

Definition of done:
- Contract compiles with no blocking error.
- Screenshot of successful compile saved.
- Contract source copied into local repo.

### Day 2

**Goal:** Deploy the vault to Polygon Amoy.

Tasks:
- Add Polygon Amoy to MetaMask.
- Get test MATIC from faucet.
- Prepare mock USDC or test token setup.
- Deploy contract through Remix.
- Save contract address in Notion and markdown logs.

Definition of done:
- Contract address exists on testnet.
- You can open explorer page.
- Deployment tx hash saved.

### Day 3

**Goal:** Finish vault interaction basics.

Tasks:
- Test deposit flow.
- Test withdraw flow.
- Confirm vault shares mint correctly.
- Confirm event emissions show up correctly.
- Document current contract limitations.

Definition of done:
- One successful deposit and one successful withdraw are recorded.
- A short issue list exists for next contract revision.

### Day 4

**Goal:** Harden the vault to MVP level.

Tasks:
- Add performance fee variable.
- Add management fee placeholder or documented stub.
- Restrict logging functions with `onlyAgent`.
- Add simple emergency / pause note if not implemented.
- Write comments explaining what is real vs. prototype-only.

Definition of done:
- Contract reflects final project MVP boundaries.
- You know exactly what is included and excluded.

---

## Sprint B — Market Data Pipe

### Day 5

**Goal:** Prove Polymarket data pipe works.

Tasks:
- Set up Python venv.
- Install `py-clob-client`, `pandas`, `python-dotenv`.
- Write `test_connection.py`.
- Pull active markets.
- Filter BTC 15m related markets.

Definition of done:
- Script prints relevant BTC 15m markets.
- Environment setup is reproducible from a README note.

### Day 6

**Goal:** Turn raw market data into usable trading inputs.

Tasks:
- Parse market question.
- Extract implied YES / NO odds.
- Save one cleaned CSV of BTC 15m markets.
- Add fields: timestamp, market question, odds, slug, condition / token id.

Definition of done:
- Clean CSV exists.
- You can explain each column.

### Day 7

**Goal:** Build the first signal script.

Tasks:
- Define the 7-minute momentum signal.
- Define the mispricing threshold rule.
- Produce `signal = trade / no trade` output.
- Keep output textual and simple.

Definition of done:
- For at least one market, the script outputs a signal object.
- You can see `side`, `market_odds`, `ai_prob`, `edge`.

---

## Sprint C — Rule-Based AI Agent

### Day 8

**Goal:** Keep the agent extremely simple.

Agent prototype rules:
- Rule 1: Only trade when edge exceeds threshold.
- Rule 2: Position size must be capped by fractional Kelly.

Tasks:
- Write a function to estimate AI probability.
- Use LLM output only as a bounded input, not as a free-form decision maker.
- Force structured JSON output.
- Reject malformed results.

Definition of done:
- Agent returns consistent structured output.
- No live execution required.

### Day 9

**Goal:** Add Kelly sizing.

Tasks:
- Implement full Kelly formula.
- Use quarter-Kelly as default for prototype safety.
- Add max position cap.
- Add daily loss cap.
- Add “no trade” branch.

Definition of done:
- Every signal includes a size recommendation.
- The size logic can be explained in one paragraph.

### Day 10

**Goal:** Log the agent decision on-chain.

Tasks:
- Connect Python script to testnet wallet.
- Call `logPosition()` only.
- Do not prioritize live order execution yet.
- Save tx hash and decoded event fields.

Definition of done:
- One signal is written on-chain.
- Explorer shows the event.

---

## Sprint D — Dashboard MVP

### Day 11

**Goal:** Build the minimum dashboard structure.

Pages / sections:
- Vault overview
- Position log
- Strategy notes
- Risk stats placeholder

Tasks:
- Set up React or simple frontend scaffold.
- Read contract address and event log.
- Display basic vault info.

Definition of done:
- Local frontend loads.
- It can read at least one on-chain event.

### Day 12

**Goal:** Show signal transparency.

Tasks:
- Render table columns: time, market, side, market odds, AI probability, Kelly size.
- Add simple labels for “trade” vs “no trade.”
- Add one explanation panel: “Why the agent acted.”

Definition of done:
- Someone can look at the page and understand the logic.

### Day 13

**Goal:** Polish demo flow.

Tasks:
- Record the exact click path for your demo.
- Fix broken states.
- Remove unused components.
- Prepare one clean test wallet.

Definition of done:
- You can demo the full story in under 3 minutes.

### Day 14

**Goal:** Freeze MVP.

Tasks:
- Stop adding features.
- Write demo script.
- Prepare architecture diagram.
- Prepare screenshot folder.
- Prepare backup video capture.

Definition of done:
- Project is stable enough for class presentation.

---

## Daily Checklist Template

Copy this block each day:

```md
## Daily Log — [DATE]

### Ship target
- One concrete deliverable only:

### Must finish today
- [ ]
- [ ]
- [ ]

### Nice to have
- [ ]
- [ ]

### Blockers
- 

### Evidence produced
- [ ] Commit
- [ ] Screenshot
- [ ] Tx hash
- [ ] Markdown note
- [ ] CSV / JSON / ABI

### End-of-day result
- Done / Partial / Blocked

### Next action tomorrow
- 
```

---

## Weekly Priority Ladder

If time gets tight, cut in this order:

Cut first:
- Fancy dashboard styling
- Live trading execution
- Advanced RAG
- Multi-agent orchestration
- Aave idle-yield branch

Keep at all costs:
- ERC-4626-style vault concept
- Deposit / withdraw logic
- Agent decision logging
- Rule-based decision engine
- A clear explanation of why blockchain is used

---

## Red Flags

Stop and simplify immediately if any of these happen:
- You spend more time collecting links than coding.
- You try to build 5 agents before 1 rule works.
- You start redesigning the frontend before the vault is stable.
- You attempt mainnet trading before the testnet logging loop works.
- You cannot explain the current system in 5 sentences.

---

## Emergency Fallback Version

If you are behind schedule, ship this version:
- Polygon Amoy vault deployed
- Deposit / withdraw demonstrated
- Agent reads Polymarket market data
- Agent calculates one signal using threshold + quarter-Kelly
- Agent logs decision on-chain
- Frontend shows the event table

This fallback version is still coherent, demoable, and aligned with the course.

---

## Demo Narrative

Use this order in class:
1. Explain the problem: prediction markets have fragmented retail flow and inconsistent pricing.
2. Show the vault: users deposit USDC-equivalent test assets into a transparent smart contract.
3. Show the agent logic: the prototype uses rule-based AI augmentation, not black-box ML.
4. Show the on-chain log: each decision is recorded immutably.
5. Show the dashboard: the system explains what it did and why.
6. End with Phase 2: live execution, better calibration, broader market coverage.

---

## One-Line Principle

**Do not build the perfect protocol. Build the ugliest version that proves the loop works.**

---

## Phase 2 — Qlib Integration (Post-MVP)

### Trigger Condition
Do **NOT** start this phase until:
1. `PolyAlphaVault.sol` is fully functional on Amoy testnet.
2. The simple Python agent (`signal_engine.py`) successfully logs decisions on-chain.
3. The dashboard can read and display these events.
4. Week 12 presentation is completed.

### Phase 2 Goals
- **Goal 1**: Transform the Becker dataset into Qlib binary format.
- **Goal 2**: Train an LSTM/LightGBM model in Qlib to predict YES-probability deviation.
- **Goal 3**: Export static rules/weights from Qlib to replace the simple threshold in `signal_engine.py`.
- **Reference**: See `Qlib_Evaluation_Report_PolyAlpha.md` for the full architectural justification.
