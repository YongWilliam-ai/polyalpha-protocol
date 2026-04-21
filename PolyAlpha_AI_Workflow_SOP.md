# PolyAlpha_AI_Workflow_SOP

## Purpose

This document defines how AI tools are used inside PolyAlpha.
It exists to prevent chaos, duplicated work, and fake progress.
Every AI tool must have a clear job, clear inputs, and clear outputs.

Core principle:
- AI does not replace judgment.
- AI accelerates research, coding, structuring, and explanation.
- Final system design decisions stay with you.

---

## Operating Philosophy

Use AI like a small startup team:
- One AI for architecture and coding
- One AI for repo / document digestion
- One AI for research synthesis
- One AI for polishing, reframing, and communication

Do **not** use all tools for the same task.
That creates noise, not leverage.

---

## AI Stack

## Tool 1 — Claude Code

### Best use
- Solidity contract drafting
- Python agent skeletons
- Refactoring code into cleaner modules
- Turning rough specifications into implementation-ready code

### Not ideal for
- Very broad market research
- Rapid comparison of many external links
- Final wording of professor-facing documents

### Inputs Claude should receive
- Exact file name
- Exact function requirements
- Constraints
- What is prototype vs. future scope

### Output format you want
- Production-style code
- Inline comments
- No vague placeholders
- Short explanation of architecture decisions

### Prompt template

```text
You are helping me build PolyAlpha, a Web3 + AI final project.

Task:
Write [FILE NAME] in [LANGUAGE].

Project constraints:
- Vault first, AI second, dashboard third
- Prototype only; testnet only
- Rule-based AI with OpenAI augmentation, not ML training
- Keep code minimal, modular, and explainable

Requirements:
- [Requirement 1]
- [Requirement 2]
- [Requirement 3]

Output rules:
- Return complete code
- No placeholders like TODO or omitted logic
- Add short inline comments only where necessary
- After code, explain the file in 5 bullets
```

---

## Tool 2 — Monica / General README Analyzer

### Best use
- Reading GitHub repos fast
- Summarizing README logic
- Extracting each repo’s edge, weakness, and reusable components
- Comparing multiple open-source projects in one sitting

### Not ideal for
- Writing final code directly into your project
- Making precise Solidity security decisions
- Producing final architecture without your review

### Inputs Monica should receive
- README text or repo link
- Specific analysis questions
- Reuse-oriented framing

### Output format you want
- Edge
- Weakness
- Reusable modules
- What to ignore
- What to copy

### Prompt template

```text
Analyze this repo for my project PolyAlpha.

I do NOT want a generic summary.
I want:
1. What is the repo’s real edge?
2. Why does it still fail to become a strong business or strategy?
3. Which parts can I directly reuse in my prototype?
4. Which parts are overbuilt and should be ignored?
5. If I only have 2 hours, what should I read first?

Return your answer in this format:
- Core edge
- Core weakness
- Reusable code
- Ignore list
- My best upgrade path
```

---

## Tool 3 — ChatGPT / Research Synthesizer

### Best use
- Turning messy notes into structure
- Creating execution plans
- Comparing strategic options
- Building dashboards, checklists, SOPs, docs, report sections
- Explaining concepts in plain English or Chinese

### Not ideal for
- Blindly generating final code without constraints
- Acting as if research is complete when data is weak

### Inputs ChatGPT should receive
- Your current project state
- Current blockers
- Desired file output
- The exact audience: professor, judges, users, yourself

### Output format you want
- Clear sections
- Bullet logic
- Decision-oriented writing
- No inflated marketing language

### Prompt template

```text
I am building PolyAlpha, a final project that combines a vault smart contract, a rule-based AI agent, and a dashboard for Polymarket research/trading signals.

Current state:
- [current progress]
- [current blocker]

Task:
Write a clean markdown file for [target document].

Requirements:
- Be concrete, not motivational
- Assume I am a solo builder with limited time
- Separate MVP vs Phase 2 clearly
- Write in a way I can paste into Notion directly

Output format:
- Use markdown headings
- Use bullet points where action matters
- Avoid generic startup clichés
```

---

## Tool 4 — Cursor / IDE Copilot Layer

### Best use
- Editing files quickly
- Refactoring local project code
- Generating helper functions inside an existing repo
- Debugging small code sections
- Making repetitive edits faster

### Not ideal for
- High-level strategy
- Large ambiguous prompts
- Trusting security-critical Solidity output without review

### Rules for Cursor use
- Only use Cursor after the file structure is decided.
- Give it one file or one bug at a time.
- Never ask it to “build everything.”
- Review all security-sensitive output manually.

### Prompt template

```text
In this existing file, make the smallest possible change to achieve the following:
- [goal]

Constraints:
- Do not rewrite unrelated sections
- Preserve current naming style
- Keep it testnet / MVP scope only
- Explain exactly what changed after the code
```

---

## Standard Workflow

## Phase 1 — Understand before building

Use this order:
1. Monica / repo analyzer reads repos.
2. ChatGPT synthesizes findings into a research note.
3. You decide what enters MVP.
4. Claude writes the first clean implementation.
5. Cursor helps edit locally.

---

## Phase 2 — Build with constrained prompts

For every file:
1. Define file purpose in one sentence.
2. Define what is in scope.
3. Define what is out of scope.
4. Generate first draft.
5. Review manually.
6. Test.
7. Only then move to next file.

File-by-file order for PolyAlpha:
- `PolyAlphaVault.sol`
- `test_connection.py`
- `signal_engine.py`
- `log_position.py`
- frontend event reader
- dashboard UI files
- report / docs

---

## Phase 3 — Research loop

When researching a new idea, always force this structure:
- What problem does this solve?
- Is it needed for MVP?
- Can I ship without it?
- Does it improve grade, demo, or business value?
- Is it a Week 12 feature or a summer feature?

If it fails this filter, it goes to Phase 2 / later list.

---

## Artifact Rules

Every AI interaction should create one of these:
- A code file
- A markdown file
- A checklist
- A table of decisions
- A clean prompt template
- A bugfix patch

If an AI chat produces only “ideas” and no artifact, it probably did not help enough.

---

## Prompt Engineering Rules

Use these six rules every time:

1. Give context first.
- Example: “This is a solo final project, testnet only, vault first.”

2. Define the exact output.
- Example: “Return one markdown file with 5 sections.”

3. Separate MVP from future scope.
- Example: “Do not include live execution.”

4. Force structured outputs.
- JSON, tables, bullet sections, exact file content.

5. Ban vague placeholders.
- Explicitly say: “No TODO, no omitted logic.”

6. Ask for tradeoffs.
- Example: “What is the simplest safe version?”

---

## File Handoff Format

When switching from one AI to another, paste this block:

```text
Project: PolyAlpha
Stage: [current stage]
Goal right now: [single immediate goal]
Already completed:
- [x]
- [x]
- [x]

Current constraints:
- Testnet only
- Vault first, AI second, dashboard third
- Rule-based agent, 1–2 rules only
- Prefer logging over live execution

Current blocker:
- [blocker]

What I need from you:
- [specific file / answer / code]

Out of scope:
- [items to avoid]
```

---

## PolyAlpha-Specific Standard Prompts

## Prompt A — Vault file

```text
Write a clean Solidity file named PolyAlphaVault.sol for a testnet-only prototype.

Requirements:
- Solidity ^0.8.20
- ERC-4626 vault style
- deposit / withdraw support
- owner access control
- agent address with onlyAgent modifier
- PositionLogged event with marketQuestion, amountUSDC, impliedOdds, aiProbability, side, kellyFraction, timestamp
- Safe and simple structure

Constraints:
- This is an MVP for a university final project
- Do not add unnecessary complexity
- No mainnet assumptions
- No placeholder functions

After code, explain:
1. What functions exist
2. What is missing for production
3. What I should test first in Remix
```

## Prompt B — Signal engine

```text
Write a Python file named signal_engine.py.

Purpose:
Read Polymarket market data and output a structured signal for BTC 15m markets.

Rules:
- Use a simple edge threshold rule
- Use quarter-Kelly sizing
- Return structured JSON-like dict output
- Include no-trade branch
- Keep the file under MVP complexity

Constraints:
- Read-only market data first
- No real order execution
- Clear function boundaries
```

## Prompt C — Repo digestion

```text
I am researching open-source Polymarket tools for PolyAlpha.

Analyze this repo for:
- actual edge
- actual weakness
- code worth reusing
- what should not enter MVP
- whether it helps vault / agent / dashboard

Return a decision-oriented answer, not a marketing summary.
```

## Prompt D — Report writing

```text
Turn my rough notes into a final-project report section.

Audience:
Professor in a blockchain business applications course.

Requirements:
- concrete
- realistic
- no hype
- explain why blockchain is used
- explain which data is on-chain vs off-chain
- explain limitations honestly
```

---

## Quality Control

Before accepting any AI output, check:
- Is this concrete?
- Is this aligned with MVP?
- Is this technically believable?
- Is this more useful than writing it myself?
- Can I test it today?

Reject output that is:
- Too long and vague
- Overengineered
- Full of future features
- Pretending prototype code is production-ready when it is not

---

## Anti-Patterns

Do not let AI drag you into these traps:
- “Let’s build a full multi-agent system first.”
- “Let’s add autonomous execution before on-chain logging works.”
- “Let’s train a model.”
- “Let’s redesign the UI before the data pipe works.”
- “Let’s keep researching one more day.”

These are delay mechanisms disguised as ambition.

---

## Decision Rights

Use this final authority structure:
- You decide scope.
- Smart contract correctness beats AI cleverness.
- Demo reliability beats feature count.
- Logged, explainable signals beat black-box intelligence.
- A smaller working system beats a larger imagined one.

---

## One-Line Rule

**Every AI conversation must reduce uncertainty or produce an artifact. Otherwise, stop using it.**
