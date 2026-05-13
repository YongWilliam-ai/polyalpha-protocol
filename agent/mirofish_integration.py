"""
mirofish_integration.py -- Real MiroFish swarm intelligence for PolyAlpha Protocol

Inspired by MiroFish (github.com/666ghj/MiroFish): diverse AI personas + Zep memory
+ LLM reasoning produce a probability-weighted market consensus.

Three public entry points:
  generate_trader_personas(market_question, count=5)
  setup_zep_memory(personas, market_context)  -> session_map dict
  get_mirofish_swarm_consensus(market_question, market_context) -> consensus dict

Env vars (read from .env at project root):
  LLM_API_KEY    -- API key for B.ai unified bridge (routes to GLM-5.1 / Claude 4.6 / GPT-5.5)
  LLM_BASE_URL   -- B.ai base URL (default: https://api.b.ai/v1) or Zhipu direct
  LLM_MODEL_NAME -- model name via B.ai routing, e.g. glm-4-flash (high-vol), glm-5.1 (reasoning)
  ZEP_API_KEY    -- Zep Cloud API key (CAMEL-OASIS memory layer)
"""

import json
import logging
import os
import uuid

import requests

try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
except ImportError:
    pass

log = logging.getLogger("mirofish")

LLM_API_KEY    = os.getenv("LLM_API_KEY", "")
# B.ai unified bridge: routes to GLM-5.1, Claude 4.6 Sonnet, or GPT-5.5 based on model name
# Fallback: Zhipu direct API for GLM-4-Flash (high-frequency, low-cost tasks)
LLM_BASE_URL   = os.getenv("LLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4/")
# Default to glm-4-flash for cost efficiency; override via .env for specific personas
# Persona routing (configured in .env or B.ai dashboard):
#   DataDrivenDave, MomentumMike  -> glm-4-flash  ($0.06/1M tokens, high speed)
#   RiskAverseRita, ContrarianCarl -> claude-4-6-sonnet (strong logical reasoning)
#   TrendFollowerTina              -> gpt-5.5 (broad context synthesis)
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "glm-4-flash")
ZEP_API_KEY    = os.getenv("ZEP_API_KEY", "")

GAMMA_API = "https://gamma-api.polymarket.com"

# Default persona definitions used as fallback when LLM persona generation fails
_DEFAULT_PERSONAS = [
    {
        "name": "ContrarianCarl",
        "style": "contrarian quantitative trader who fades crowd consensus and bets against obvious outcomes",
        "bias": "skeptical of high-probability markets, hunts for mispriced tail risks",
        "weight": 0.20,
    },
    {
        "name": "TrendFollowerTina",
        "style": "momentum and trend-following trader who rides directional price signals",
        "bias": "follows recent market direction and volume momentum",
        "weight": 0.20,
    },
    {
        "name": "ValueInvestorVictor",
        "style": "fundamental value investor who anchors to historical base rates and ignores short-term noise",
        "bias": "trusts data-driven base rates over recent sentiment",
        "weight": 0.25,
    },
    {
        "name": "MacroAnalystMaria",
        "style": "macro analyst who evaluates geopolitical events, central bank policy, and systemic risk",
        "bias": "considers exogenous macro factors most market participants overlook",
        "weight": 0.20,
    },
    {
        "name": "OnChainSleuth",
        "style": "on-chain data analyst who studies smart money flows, liquidity depth, and blockchain metrics",
        "bias": "follows institutional wallet positioning and on-chain accumulation signals",
        "weight": 0.15,
    },
]


# ---------------------------------------------------------------------------
# Public helper
# ---------------------------------------------------------------------------

def fetch_market_question(condition_id: str) -> str:
    """Return the human-readable question for a Polymarket condition ID."""
    try:
        resp = requests.get(
            f"{GAMMA_API}/markets",
            params={"condition_ids": condition_id},
            timeout=6,
        )
        resp.raise_for_status()
        data = resp.json()
        if data and isinstance(data, list):
            return data[0].get("question", condition_id)
    except Exception:
        pass
    return condition_id


# ---------------------------------------------------------------------------
# Step 1: generate personas
# ---------------------------------------------------------------------------

def generate_trader_personas(market_question: str, count: int = 5) -> list[dict]:
    """
    Use the LLM to generate `count` distinct quantitative trader personas
    tailored to a specific prediction market question.

    Returns a list of dicts with keys: name, style, bias, weight.
    Falls back to _DEFAULT_PERSONAS if LLM is unavailable or parsing fails.
    """
    if not LLM_API_KEY:
        log.warning("LLM_API_KEY not set -- using default personas")
        return _DEFAULT_PERSONAS[:count]

    try:
        from openai import OpenAI
        client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)

        prompt = (
            f"You are building a multi-agent prediction market analysis swarm.\n"
            f"Market question: {market_question}\n\n"
            f"Generate exactly {count} distinct quantitative trader personas that would analyze "
            f"this market from fundamentally different angles.\n"
            f"Each persona should have a genuinely different analytical philosophy.\n\n"
            f"Return ONLY a valid JSON array with {count} objects. Each object must have:\n"
            f"  name: string (creative 2-word trader alias like 'ContrarianCarl')\n"
            f"  style: string (1 sentence describing their analytical approach)\n"
            f"  bias: string (1 sentence on their systematic bias for THIS specific question)\n"
            f"  weight: float (their relative weighting, values must sum to 1.0)\n"
            f"Return ONLY the JSON array. No markdown, no explanation."
        )

        resp = client.chat.completions.create(
            model=LLM_MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=900,
        )

        content = resp.choices[0].message.content.strip()
        # Strip markdown code fences if present
        if "```" in content:
            parts = content.split("```")
            content = parts[1] if len(parts) >= 2 else content
            if content.lower().startswith("json"):
                content = content[4:]

        personas = json.loads(content.strip())

        # Normalize weights to sum to exactly 1.0
        total_w = sum(float(p.get("weight", 0.2)) for p in personas)
        if total_w > 0:
            for p in personas:
                p["weight"] = round(float(p.get("weight", 0.2)) / total_w, 4)

        log.info(f"LLM generated {len(personas)} personas for: {market_question[:60]}")
        return personas

    except Exception as exc:
        log.warning(f"generate_trader_personas failed ({exc}) -- using defaults")
        return _DEFAULT_PERSONAS[:count]


# ---------------------------------------------------------------------------
# Step 2: Zep memory setup
# ---------------------------------------------------------------------------

def setup_zep_memory(personas: list[dict], market_context: str) -> dict[str, str]:
    """
    Create a Zep user and session for each persona, then seed their memory
    with the market context so it informs their LLM reasoning.

    Returns: {persona_name: session_id, ...}
    Returns empty dict gracefully if Zep is unavailable.
    """
    if not ZEP_API_KEY:
        log.warning("ZEP_API_KEY not set -- skipping Zep memory injection")
        return {}

    session_map: dict[str, str] = {}

    try:
        from zep_cloud.client import Zep
        from zep_cloud import Message

        zep    = Zep(api_key=ZEP_API_KEY)
        run_id = uuid.uuid4().hex[:8]

        for persona in personas:
            safe = persona["name"].lower().replace(" ", "_")
            user_id    = f"polyalpha_{safe}_{run_id}"
            session_id = f"sess_{safe}_{run_id}"

            # Create user (ignore if exists)
            try:
                zep.user.add(user_id=user_id, first_name=persona["name"])
            except Exception:
                pass

            # Create session
            try:
                zep.memory.add_session(session_id=session_id, user_id=user_id)
            except Exception:
                pass

            # Seed memory with persona identity + market context
            system_content = (
                f"You are {persona['name']}, a {persona['style']}.\n"
                f"Your analytical bias: {persona['bias']}\n"
                f"Current market context for your analysis:\n{market_context}"
            )
            try:
                zep.memory.add(
                    session_id=session_id,
                    messages=[
                        Message(role="system", content=system_content, role_type="system")
                    ],
                )
                session_map[persona["name"]] = session_id
                log.info(f"  Zep memory seeded: {persona['name']} -> {session_id}")
            except Exception as exc:
                log.warning(f"  Zep memory.add failed for {persona['name']}: {exc}")

    except ImportError:
        log.warning("zep-cloud not installed -- skipping Zep memory")
    except Exception as exc:
        log.warning(f"setup_zep_memory error: {exc}")

    return session_map


def _retrieve_zep_context(session_id: str) -> str:
    """Retrieve condensed memory context from Zep for a session."""
    if not ZEP_API_KEY or not session_id:
        return ""
    try:
        from zep_cloud.client import Zep
        zep    = Zep(api_key=ZEP_API_KEY)
        memory = zep.memory.get(session_id=session_id)
        return getattr(memory, "context", "") or ""
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# Step 3: per-persona LLM vote
# ---------------------------------------------------------------------------

def _persona_vote(persona: dict, market_question: str, zep_context: str) -> dict:
    """
    Ask the LLM to role-play as `persona` and vote YES/NO on `market_question`.

    Returns dict:
      persona, vote ("YES"|"NO"|"ABSTAIN"), confidence (0-100),
      reasoning (str), weight (float), estimate (float 0-1)
    """
    if not LLM_API_KEY:
        # Deterministic fallback seeded by persona name + question hash
        import hashlib
        seed    = int(hashlib.sha256(f"{market_question}:{persona['name']}".encode()).hexdigest()[:8], 16)
        prob    = (seed / 0xFFFFFFFF) * 0.60 + 0.20   # range 0.20 – 0.80
        vote    = "YES" if prob > 0.50 else "NO"
        return {
            "persona":    persona["name"],
            "vote":       vote,
            "confidence": int(prob * 100),
            "reasoning":  "LLM unavailable -- deterministic fallback",
            "weight":     persona.get("weight", 0.20),
            "estimate":   round(prob, 3),
        }

    try:
        from openai import OpenAI
        client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)

        system_msg = (
            f"You are {persona['name']}, a {persona['style']}.\n"
            f"Your systematic analytical bias: {persona['bias']}\n"
        )
        if zep_context:
            system_msg += f"\nYour retrieved memory context:\n{zep_context}\n"

        user_msg = (
            f"Prediction market question: {market_question}\n\n"
            f"Based on your persona, analytical style, and memory context, "
            f"vote on whether this market will resolve YES.\n\n"
            f"Respond with ONLY this JSON object (no markdown):\n"
            f'{{"vote": "YES" or "NO", "confidence": <integer 1-100>, '
            f'"reasoning": "<one concise sentence>"}}'
        )

        resp = client.chat.completions.create(
            model=LLM_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user",   "content": user_msg},
            ],
            temperature=0.5,
            max_tokens=200,
        )

        raw = resp.choices[0].message.content.strip()
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.lower().startswith("json"):
                raw = raw[4:]

        result     = json.loads(raw.strip())
        vote       = str(result.get("vote", "NO")).upper()
        confidence = max(1, min(100, int(result.get("confidence", 50))))
        reasoning  = str(result.get("reasoning", ""))

        # Convert vote + confidence to a 0-1 probability estimate
        estimate = (confidence / 100.0) if vote == "YES" else (1.0 - confidence / 100.0)

        return {
            "persona":    persona["name"],
            "vote":       vote,
            "confidence": confidence,
            "reasoning":  reasoning,
            "weight":     persona.get("weight", 0.20),
            "estimate":   round(estimate, 3),
        }

    except Exception as exc:
        log.warning(f"  LLM vote failed for {persona['name']}: {exc}")
        return {
            "persona":    persona["name"],
            "vote":       "ABSTAIN",
            "confidence": 50,
            "reasoning":  f"API error: {exc}",
            "weight":     persona.get("weight", 0.20),
            "estimate":   0.50,
        }


# ---------------------------------------------------------------------------
# Main public function
# ---------------------------------------------------------------------------

def get_mirofish_swarm_consensus(market_question: str, market_context: str = "") -> dict:
    """
    Full MiroFish swarm consensus pipeline:

    1. generate_trader_personas  -- LLM creates 5 distinct analysts
    2. setup_zep_memory          -- injects market context into each persona's memory
    3. _retrieve_zep_context     -- each persona retrieves their memory
    4. _persona_vote             -- each persona votes YES/NO via LLM
    5. Weighted aggregation      -- consensus score + label

    Returns:
    {
      "market_question": str,
      "consensus":       float,   # 0.0 – 1.0
      "label":           str,     # SWARM_STRONG_BUY / BUY / HOLD / SELL / STRONG_SELL
      "votes":           list[dict],
      "interview_logs":  list[str],
      "source":          "live" | "fallback"
    }
    """
    context = market_context or market_question

    personas    = generate_trader_personas(market_question)
    session_map = setup_zep_memory(personas, context)

    votes:          list[dict] = []
    interview_logs: list[str]  = []
    source = "live" if LLM_API_KEY else "fallback"

    for persona in personas:
        session_id  = session_map.get(persona["name"], "")
        zep_context = _retrieve_zep_context(session_id)
        v           = _persona_vote(persona, market_question, zep_context)
        votes.append(v)
        interview_logs.append(
            f"[{v['persona']}] {v['vote']} @ {v['confidence']}% -- {v['reasoning']}"
        )
        log.info(f"  {v['persona']}: {v['vote']} @ {v['confidence']}% ({v['reasoning'][:60]})")

    consensus = round(sum(v["estimate"] * v["weight"] for v in votes), 3)

    if   consensus >= 0.80: label = "SWARM_STRONG_BUY"
    elif consensus >= 0.65: label = "SWARM_BUY"
    elif consensus >= 0.35: label = "SWARM_HOLD"
    elif consensus >= 0.20: label = "SWARM_SELL"
    else:                   label = "SWARM_STRONG_SELL"

    return {
        "market_question": market_question,
        "consensus":       consensus,
        "label":           label,
        "votes":           votes,
        "interview_logs":  interview_logs,
        "source":          source,
    }
