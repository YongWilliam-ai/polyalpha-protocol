# PolyAlpha_Notion_Database_Schema

## Purpose

This file defines the Notion workspace structure for PolyAlpha.
The goal is simple: one operating system for research, build progress, repo analysis, AI workflow, and final-project reporting.

This is not meant to be pretty.
It is meant to make sure you always know:
- what the current goal is,
- what is blocked,
- what artifact was produced,
- and what should happen next.

---

## Workspace Principle

PolyAlpha should be run like a tiny operating company.
That means your Notion should not be one long page.
It should be a small database system with linked views.

Core operating rule:
- **Projects are stable**
- **Tasks move daily**
- **Research accumulates**
- **Signals get logged**
- **Decisions are written down**

---

## Recommended Workspace Structure

Create one top-level Notion page:

`PolyAlpha OS`

Inside it, create these 8 databases:
1. Project Control
2. Sprint Tasks
3. Daily Logs
4. Research Library
5. Repo Analysis
6. AI Prompt Ops
7. Build Artifacts
8. Signal / Experiment Log

Optional later:
9. Report Writing
10. Presentation Assets

---

## Database 1 — Project Control

### Purpose
One-row-or-few-row control center for the whole project.
This is where you track the current phase, current blocker, and top priority.

### Recommended properties

| Property | Type | Purpose |
|---|---|---|
| Project Name | Title | Usually `PolyAlpha` |
| Stage | Select | Idea / Vault / Agent / Dashboard / Demo / Report |
| Status | Select | Active / Blocked / Paused / Done |
| Current Goal | Text | Single highest-priority objective |
| Current Blocker | Text | Biggest reason progress may stop |
| MVP Scope | Text | What the prototype must include |
| Out of Scope | Text | Things intentionally excluded |
| Demo Date | Date | Class presentation / internal demo |
| Professor Update Sent? | Checkbox | Whether progress update was sent |
| Confidence | Number | 1–10 self-rating |
| Last Review | Date | Last weekly review date |
| Notes | Text | Short control notes |

### Main views
- Master control
- Active only
- Blocked view

### Sample row
- Project Name: PolyAlpha
- Stage: Vault
- Status: Active
- Current Goal: Deploy working ERC-4626-style vault on Polygon Amoy
- Current Blocker: Need mock USDC setup and contract test flow

---

## Database 2 — Sprint Tasks

### Purpose
This is the execution engine.
Every concrete thing you need to do goes here.

### Recommended properties

| Property | Type | Purpose |
|---|---|---|
| Task | Title | Concrete action item |
| Status | Status | Not started / In progress / Waiting / Done |
| Priority | Select | P0 / P1 / P2 |
| Area | Select | Vault / Agent / Dashboard / Research / Report / Demo |
| Sprint | Select | Sprint A / B / C / D |
| Due | Date | Deadline |
| Est. Hours | Number | Time estimate |
| Actual Hours | Number | Time spent |
| Depends On | Relation -> Sprint Tasks | Dependency tracking |
| Linked Project | Relation -> Project Control | Connect to main project |
| Artifact Needed | Select | Code / Screenshot / Tx hash / CSV / Markdown / Video |
| Definition of Done | Text | Objective completion rule |
| Owner | Person or Text | Usually you |
| Notes | Text | Quick context |

### Main views
- Kanban by Status
- Calendar by Due
- P0 tasks only
- Vault only
- This week

### Rules
- Every task must start with a verb.
- Every P0 task must have a definition of done.
- No task should be larger than 3 hours unless you split it.

### Sample tasks
- Compile `PolyAlphaVault.sol` in Remix
- Deploy contract to Polygon Amoy
- Write `test_connection.py`
- Parse BTC 15m markets into CSV
- Implement quarter-Kelly function
- Log first agent decision on-chain
- Build dashboard event table

---

## Database 3 — Daily Logs

### Purpose
This prevents fake progress.
Each day should show what you intended to ship, what happened, and what evidence exists.

### Recommended properties

| Property | Type | Purpose |
|---|---|---|
| Log Title | Title | Example: `2026-04-09 Daily Log` |
| Date | Date | Log date |
| Ship Target | Text | One concrete output only |
| Result | Select | Done / Partial / Blocked |
| Energy | Number | 1–10 personal energy |
| Deep Work Blocks | Number | Count of focused sessions |
| Main Blocker | Text | Biggest obstacle today |
| Next Action | Text | First action tomorrow |
| Related Tasks | Relation -> Sprint Tasks | What you worked on |
| Artifact Links | Relation -> Build Artifacts | Proof of output |
| Notes | Text | Reflection or issue note |

### Template inside each page

```md
## Ship target
- 

## Must finish today
- [ ]
- [ ]
- [ ]

## Evidence produced
- 

## What got blocked
- 

## Next action tomorrow
- 
```

### Main views
- Calendar
- Last 7 days
- Blocked days only

---

## Database 4 — Research Library

### Purpose
All external material goes here: GitHub repos, docs, X posts, articles, papers, dashboards, tools.
This is the input layer for your thinking.

### Recommended properties

| Property | Type | Purpose |
|---|---|---|
| Resource | Title | Name of source |
| Type | Select | GitHub / X / Docs / Website / Paper / Dataset / Video |
| URL | URL | Link |
| Topic | Multi-select | Vault / Polymarket / AI / Web4 / Kelly / Dashboard |
| Usefulness | Select | High / Medium / Low |
| Status | Select | Unread / Reading / Processed / Archived |
| Why It Matters | Text | One-line reason |
| Key Insight | Text | What it taught you |
| Reusable For | Multi-select | Vault / Agent / Dashboard / Report |
| Added On | Date | Date saved |
| Related Repo Analysis | Relation -> Repo Analysis | If applicable |
| Notes | Text | Extra detail |

### Main views
- Unread inbox
- High usefulness
- GitHub only
- Papers / research only
- Dashboard inspiration

### Rules
- Do not save a link without writing `Why It Matters`.
- If a source is not useful after reading, archive it.
- Each important source should be converted into either a task, a decision, or a repo-analysis entry.

---

## Database 5 — Repo Analysis

### Purpose
This is where you break down open-source repos into practical value.
It stops you from forgetting which repo had what edge.

### Recommended properties

| Property | Type | Purpose |
|---|---|---|
| Repo Name | Title | Repository name |
| URL | URL | GitHub link |
| Category | Select | Bot / SDK / CLI / Dashboard / Infra / Memory / Agent |
| Edge | Text | What this repo does well |
| Weakness | Text | Main limit |
| Reusable Module | Text | What you can actually reuse |
| Ignore | Text | What not to copy |
| MVP Relevance | Select | Critical / Useful / Optional / No |
| Read Depth | Select | README only / Light code / Deep code |
| Status | Select | To review / Reviewed / Reused / Archived |
| Related Resources | Relation -> Research Library | Supporting sources |
| Related Tasks | Relation -> Sprint Tasks | Follow-up work |
| Notes | Text | Final judgment |

### Main views
- Critical repos
- Reviewed repos
- Reuse now
- Ignore / archive

### Suggested starter entries
- `Polymarket/polymarket-cli`
- `Polymarket/py-clob-client`
- `Polymarket/agents`
- `cakaroni/polymarket-arbitrage-bot-btc-eth-15m`
- `infraform/polymarket-arbitrage-trading-bot`
- `Gabagool2-2/polymarket-trading-bot-python`
- `openai/codex-plugin-cc`
- `numman-ali/openskills`

---

## Database 6 — AI Prompt Ops

### Purpose
This is the command center for how you use AI tools.
You should be able to see which prompt produced which artifact.

### Recommended properties

| Property | Type | Purpose |
|---|---|---|
| Prompt Name | Title | Name of prompt workflow |
| Tool | Select | Claude / ChatGPT / Monica / Cursor / Other |
| Goal | Text | What the prompt is supposed to do |
| Input Context | Text | What context was given |
| Prompt Text | Text | Full prompt or summary |
| Output Type | Select | Code / Markdown / Summary / Table / Debug |
| Result Quality | Select | Strong / Okay / Weak |
| Reusable? | Checkbox | Worth keeping as template |
| Linked Artifact | Relation -> Build Artifacts | What it created |
| Related Task | Relation -> Sprint Tasks | Why it was used |
| Notes | Text | Lessons learned |

### Main views
- Reusable prompts
- Claude prompts
- Weak prompts to rewrite
- Prompt → artifact map

### Rule
If a prompt does not create a usable artifact or reduce uncertainty, mark it weak and do not reuse it.

---

## Database 7 — Build Artifacts

### Purpose
This is your proof layer.
Every meaningful output should be recorded here.

### Recommended properties

| Property | Type | Purpose |
|---|---|---|
| Artifact | Title | Name of output |
| Type | Select | Solidity / Python / Markdown / CSV / Screenshot / Tx Hash / UI / Video |
| File / Link | URL or Files | Storage reference |
| Status | Select | Draft / Working / Verified / Obsolete |
| Related Area | Select | Vault / Agent / Dashboard / Report / Demo |
| Created On | Date | Creation date |
| Version | Text | v0.1 / v0.2 etc. |
| Source AI Tool | Select | Claude / ChatGPT / Cursor / Manual / Mixed |
| Related Task | Relation -> Sprint Tasks | What produced it |
| Related Daily Log | Relation -> Daily Logs | When it was produced |
| Verification Method | Text | Compile / Test / Explorer / Manual Review |
| Notes | Text | Observations |

### Main views
- Latest verified
- Contract artifacts
- Demo assets
- Needs verification

### Examples
- `PolyAlphaVault.sol v0.1`
- `signal_engine.py v0.1`
- `BTC_15m_markets_clean.csv`
- `Amoy deployment tx hash`
- `Dashboard event table screenshot`
- `Final demo script`

---

## Database 8 — Signal / Experiment Log

### Purpose
This tracks the logic layer of the project.
Even before live execution, you should log signals, assumptions, test outputs, and experiment results.

### Recommended properties

| Property | Type | Purpose |
|---|---|---|
| Experiment / Signal | Title | Name of signal or test |
| Date | Date | When it ran |
| Market | Text | BTC 15m or other market |
| Strategy Type | Select | Momentum / Mispricing / Kelly / Arbitrage / Backtest |
| Market Odds | Number | Current market-implied probability |
| AI Probability | Number | Agent estimate |
| Edge | Number | AI Prob - Market Odds |
| Kelly Fraction | Number | Suggested size |
| Action | Select | Trade / No trade / Logged only |
| Outcome | Select | Pending / Win / Loss / Invalid |
| Why | Text | One-sentence rationale |
| Data Source | Text | CLI / SDK / manual / backtest dataset |
| Linked Artifact | Relation -> Build Artifacts | Output file or tx hash |
| Notes | Text | Caveats |

### Main views
- Latest signals
- Trade only
- No-trade decisions
- Backtest experiments
- Needs review

### Why this matters
Your final dashboard and report both become easier if every signal already has a structured log.

---

## Optional Database 9 — Report Writing

### Purpose
Use this if you want to modularize the final report instead of writing everything in one page.

### Properties
- Section Title
- Status
- Course Objective Linked
- Needs Citation?
- Draft Text
- Reviewer Notes
- Related Artifact

Suggested sections:
- Problem statement
- Why blockchain
- On-chain vs off-chain split
- Vault mechanics
- AI agent logic
- Risks and limitations
- Future work

---

## Optional Database 10 — Presentation Assets

### Purpose
This is for demo day control.
Store every slide, diagram, screenshot, and speaking order asset.

### Properties
- Asset Name
- Type
- Slide Number
- Status
- Needs Redesign?
- Related Artifact
- Speaking Point

---

## Relationship Map

Use these main relations:

- Project Control -> Sprint Tasks
- Sprint Tasks -> Daily Logs
- Sprint Tasks -> Build Artifacts
- Research Library -> Repo Analysis
- Repo Analysis -> Sprint Tasks
- AI Prompt Ops -> Build Artifacts
- Signal / Experiment Log -> Build Artifacts
- Daily Logs -> Build Artifacts

Simple logic:
- Research creates decisions.
- Decisions create tasks.
- Tasks create artifacts.
- Artifacts support demo and report.

---

## Best Home Page Layout

Inside `PolyAlpha OS`, build this dashboard layout:

### Section 1 — Control panel
Embed linked views:
- Project Control (single row)
- P0 Sprint Tasks
- Today’s Daily Log

### Section 2 — Execution
Embed linked views:
- Tasks board by status
- This week calendar
- Latest verified artifacts

### Section 3 — Intelligence
Embed linked views:
- Unread research inbox
- Critical repo analysis
- Latest signal / experiment log

### Section 4 — AI operations
Embed linked views:
- Reusable prompt library
- Weak prompts to improve

### Section 5 — Reporting
Embed linked views:
- Report sections
- Presentation assets

---

## Recommended Templates

## Template A — New Task

```md
## Objective
-

## Why this matters
-

## Definition of done
-

## Dependencies
-

## Output artifact
-
```

## Template B — New Research Entry

```md
## Why it matters
-

## Key insight
-

## What I can reuse
-

## What I will ignore
-
```

## Template C — New Repo Analysis

```md
## Core edge
-

## Core weakness
-

## Reusable now
-

## Ignore for MVP
-

## Follow-up task
-
```

## Template D — New Signal Log

```md
## Market
-

## Odds / AI estimate
-

## Edge
-

## Position logic
-

## Action
-

## Notes
-
```

---

## Operating Rules for Notion

Follow these rules strictly:
- Do not keep everything as loose notes.
- Every important note must become either a task, artifact, or research entry.
- Review Project Control once a week.
- Review Sprint Tasks every day.
- Review Research Library twice a week.
- Archive dead ideas aggressively.

If Notion becomes messy, it stops being a system and becomes a guilt wall.

---

## Minimal Version

If you want the leanest version possible, only create these 5 databases first:
1. Project Control
2. Sprint Tasks
3. Daily Logs
4. Research Library
5. Build Artifacts

That is enough to run the project.
The other databases can be added once the build loop is stable.

---

## Recommended First Setup Order

Do this in order:
1. Create `PolyAlpha OS`
2. Create `Project Control`
3. Create `Sprint Tasks`
4. Create `Daily Logs`
5. Create `Build Artifacts`
6. Add `Research Library`
7. Add `Repo Analysis`
8. Add `AI Prompt Ops`
9. Add `Signal / Experiment Log`
10. Create the home dashboard with linked views

Time required: about 45–75 minutes if done cleanly.

---

## First Rows to Add Immediately

Add these right away after setup:

### Project Control
- PolyAlpha / Stage: Vault / Status: Active

### Sprint Tasks
- Compile vault contract
- Deploy to Amoy
- Test deposit and withdraw
- Connect py-clob-client
- Save BTC 15m CSV
- Implement quarter-Kelly sizing
- Log first signal on-chain

### Research Library
- OpenZeppelin ERC-4626 docs
- Polymarket CLOB docs
- Polymarket CLI repo
- py-clob-client repo
- Polymarket agents repo

### Build Artifacts
- `PolyAlphaVault.sol`
- deployment tx hash
- `test_connection.py`
- `BTC_15m_markets_clean.csv`

---

## Final Rule

**If a page does not help you decide, build, or prove something, it does not belong in the operating system.**
