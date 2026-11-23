"""Home Care Companion MVP logic.

Deterministic-first, LLM-enhanced when available. No account actions, no messaging,
no service transactions. Respect docs/constraints.md (C1, C2, C3).
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from . import config

# ---------------------------------------------------------------------------
# Hard guard (C1/C2): no network imports / no forbidden CTA strings in source.
# The banned tokens are assembled to avoid self-matching in naive scans.
# ---------------------------------------------------------------------------
_BANNED_TEXT = [
    "bo" + "ok now",
    "bo" + "ok again",
    "cou" + "pon",
    "dis" + "count",
    "off" + "er",
    "pa" + "y now",
    "check" + "out",
]
_BANNED_IMPORTS = ["im" + "port requests", "im" + "port httpx", "im" + "port urllib", "from ur" + "llib"]


def _self_guard() -> None:
    src = Path(__file__).read_text(encoding="utf-8")
    lower = src.lower()
    for token in _BANNED_IMPORTS:
        if token in lower:
            raise AssertionError(f"Forbidden network import found: {token}")
    for token in _BANNED_TEXT:
        if token in lower:
            # allow this guard definition itself by checking occurrences outside assembled literals
            # simple fallback: if token appears, ensure it's only in _BANNED_TEXT construction
            occurrences = lower.count(token)
            constructed = lower.count('"' + token + '"') + lower.count("'" + token + "'")
            if occurrences > constructed:
                raise AssertionError(f"Forbidden string found: {token}")


_self_guard()

PROFILE_QUESTIONS = [
    {
        "id": "city_tier",
        "question": "Which city tier do you live in?",
        "type": "single",
        "options": ["Metro", "Tier 2", "Other"],
    },
    {
        "id": "home_type",
        "question": "What type of home do you live in?",
        "type": "single",
        "options": ["Apartment", "Independent house", "Other"],
    },
    {
        "id": "household",
        "question": "Who lives in the home?",
        "type": "multi",
        "options": ["Family", "Kids", "Pets", "Elderly members", "Living alone"],
    },
    {
        "id": "categories_used_before",
        "question": "Which Urban Company categories have you used before?",
        "type": "multi",
        "options": config.CORE_CATEGORIES + ["Other"],
    },
    {
        "id": "months_since_last_service",
        "question": "How many months since your last completed service?",
        "type": "single",
        "options": ["0-1", "2-3", "4-6", "7-12", "12+"],
    },
    {
        "id": "planning_style",
        "question": "How do you usually handle home maintenance?",
        "type": "single",
        "options": ["Planned", "Reactive", "Avoided until urgent"],
    },
]

ROUTES = ["DIY", "LOCAL_OR_NEIGHBOUR", "UC_CATEGORY", "WAIT_AND_WATCH", "SEEK_IMMEDIATE_HELP"]
TOOLS = [
    "ask_clarifying_question",
    "public_reference_lookup",
    "build_calendar",
    "route_need",
    "capture_reflection",
    "show_public_info",
]

URGENT_RE = re.compile(r"gas smell|sparks?|burning smell|flooding|burst pipe|water everywhere|electric shock|fire", re.I)
DIY_RE = re.compile(r"filter|wipe|clean vent|tighten|unclog|drain hair|battery|remote|dust", re.I)
LOCAL_RE = re.compile(r"society|building electrician|neighbor|neighbour|watchman|caretaker|whatsapp group|local electrician from downstairs", re.I)

CATEGORY_KEYWORDS = {
    "AC Service": ["ac", "air conditioner", "cooling", "not cooling", "ac service", "split ac"],
    "Plumbing": ["tap", "leak", "pipe", "drain", "clog", "faucet", "plumber", "water leak"],
    "Deep Cleaning": ["deep clean", "sofa clean", "bathroom clean", "kitchen clean", "mattress clean"],
    "Pest Control": ["pest", "cockroach", "ants", "termites", "mosquito", "rats"],
    "Appliance Repair": ["fridge", "refrigerator", "washing machine", "microwave", "geyser", "appliance"],
    "Salon": ["salon", "haircut", "facial", "grooming"],
}


def load_public_reference(path: str | Path | None = None) -> pd.DataFrame:
    config.ensure_dirs()
    ref_path = Path(path) if path else config.REFERENCE
    if not ref_path.exists():
        return pd.DataFrame(columns=["need", "trigger", "typical_timing_days", "public_basis", "source_url", "source_class"])
    df = pd.read_csv(ref_path)
    for col in ["need", "trigger", "typical_timing_days", "public_basis", "source_url", "source_class"]:
        if col not in df.columns:
            df[col] = ""
    df = df.fillna("")
    return df


def _profile_set(profile: dict[str, Any], key: str) -> set[str]:
    val = profile.get(key, [])
    if isinstance(val, str):
        return {v.strip().lower() for v in val.split(",") if v.strip()}
    if isinstance(val, list):
        return {str(v).strip().lower() for v in val}
    return {str(val).strip().lower()} if val else set()


def build_calendar(profile: dict[str, Any], reference: pd.DataFrame | None = None, llm: Any = None) -> list[dict[str, Any]]:
    """Build a personalized home-care calendar. Deterministic when llm is None."""
    ref = reference if reference is not None else load_public_reference()
    if ref.empty:
        return []

    cats = _profile_set(profile, "categories_used_before")
    planning = str(profile.get("planning_style", "")).lower()
    home_type = str(profile.get("home_type", "")).lower()
    household = _profile_set(profile, "household")

    scored: list[dict[str, Any]] = []
    for _, row in ref.iterrows():
        need = str(row.get("need", "")).strip()
        basis = str(row.get("public_basis", "")).strip()
        src = str(row.get("source_url", "")).strip()
        if not need or not basis or not src:
            continue
        try:
            timing = int(float(row.get("typical_timing_days", 90) or 90))
        except Exception:
            timing = 90

        score = 1.0
        need_l = need.lower()
        if "ac" in need_l and ("ac service" in cats or planning == "planned"):
            score += 2
        if "pest" in need_l and ("monsoon" in str(row.get("trigger", "")).lower()):
            score += 1.5
        if "clean" in need_l and ("deep cleaning" in cats or "family" in household):
            score += 1.2
        if "plumb" in need_l or "leak" in need_l:
            score += 1.0
        if "appliance" in need_l and "apartment" in home_type:
            score += 0.8
        if planning == "reactive":
            score += 0.3

        confidence = min(0.95, 0.45 + score / 8)
        scored.append({
            "need": need,
            "when_days": max(7, timing),
            "why": str(row.get("trigger", "")).strip() or "Routine home maintenance timing.",
            "confidence": round(confidence, 2),
            "basis": basis,
            "source_url": src,
            "route_hint": _route_hint_for_need(need),
            "score": score,
        })

    scored.sort(key=lambda x: (-x["score"], x["when_days"]))
    for item in scored:
        item.pop("score", None)
    return scored[:6]


def _route_hint_for_need(need: str) -> str:
    n = need.lower()
    if any(w in n for w in ["filter", "coil", "seal check", "alarm test"]):
        return "DIY"
    if any(w in n for w in ["electrical", "sparks", "gas"]):
        return "SEEK_IMMEDIATE_HELP"
    return "UC_CATEGORY_OR_LOCAL"


def match_core_category(text: str) -> tuple[str | None, float]:
    t = str(text or "").lower()
    best_cat = None
    best_score = 0
    for cat, kws in CATEGORY_KEYWORDS.items():
        score = sum(1 for k in kws if k in t)
        if score > best_score:
            best_score = score
            best_cat = cat
    if not best_cat or best_score == 0:
        return None, 0.0
    confidence = min(0.95, 0.55 + 0.15 * best_score)
    return best_cat, round(confidence, 2)


def _log_record(tool: str, reason: str, text: str = "", route: str = "", confidence: float = 0.0, session_hash: str = "") -> dict[str, Any]:
    return {
        "ts": datetime.now(timezone.utc).isoformat(),
        "session_hash": session_hash or hashlib.sha256(b"local-session").hexdigest()[:12],
        "turn": 0,
        "chosen_tool": tool,
        "reason": reason,
        "user_input_length": len(str(text or "")),
        "route": route,
        "confidence": confidence,
    }


def route_need(text: str, profile: dict[str, Any] | None = None, llm: Any = None, session_hash: str = "") -> dict[str, Any]:
    """Route a user need to the right next step. No service transactions."""
    profile = profile or {}
    t = str(text or "").strip()
    t_lower = t.lower()
    words = [w for w in re.split(r"\s+", t) if w]
    cat, cat_conf = match_core_category(t_lower)
    has_clear_signal = bool(URGENT_RE.search(t_lower) or DIY_RE.search(t_lower) or LOCAL_RE.search(t_lower) or cat)

    if URGENT_RE.search(t_lower):
        rec = _log_record("route_need", "Urgent safety signal detected", t, "SEEK_IMMEDIATE_HELP", 0.99, session_hash=session_hash)
        result = {
            "route": "SEEK_IMMEDIATE_HELP",
            "confidence": 0.99,
            "reason": "Safety first: this may be urgent. Seek immediate qualified help and avoid using the affected appliance/area. Why not other routes: DIY/local/UC category are not safe first steps for urgent hazards.",
            "clarifying_questions": [],
            "used_public_reference": False,
            "tool_trace": rec,
        }
        log_tool_trace(rec)
        return result

    if (len(words) < 4 and not has_clear_signal) or not re.search(r"[a-zA-Z]", t_lower) or (len(words) < 12 and not has_clear_signal):
        rec = _log_record("ask_clarifying_question", "Input too vague to route safely", t, "ASK", 0.2, session_hash=session_hash)
        result = {
            "route": "WAIT_AND_WATCH",
            "confidence": 0.2,
            "reason": "I need a bit more detail before suggesting a route. Why not other routes: recommending DIY or a professional now could be wrong without context.",
            "clarifying_questions": [
                "What exactly is not working or concerning you?",
                "When did you first notice it, and has it changed recently?",
            ],
            "used_public_reference": False,
            "tool_trace": rec,
        }
        log_tool_trace(rec)
        return result

    if DIY_RE.search(t_lower) and not URGENT_RE.search(t_lower):
        rec = _log_record("route_need", "Simple maintenance signal detected", t, "DIY", 0.78, session_hash=session_hash)
        result = {
            "route": "DIY",
            "confidence": 0.78,
            "reason": "This looks like small routine maintenance you may be able to handle safely. Why not other routes: local/UC help may be unnecessary for a simple task; waiting may let a small issue grow.",
            "clarifying_questions": [],
            "used_public_reference": False,
            "steps": [
                "Turn off the appliance or water source if relevant.",
                "Use basic cleaning/tightening only if safe and accessible.",
                "Stop and seek qualified help if you notice damage, sparks, burning smell, or leaks.",
            ],
            "tool_trace": rec,
        }
        log_tool_trace(rec)
        return result

    if LOCAL_RE.search(t_lower):
        rec = _log_record("route_need", "Neighbourhood/building-level task signal", t, "LOCAL_OR_NEIGHBOUR", 0.74, session_hash=session_hash)
        result = {
            "route": "LOCAL_OR_NEIGHBOUR",
            "confidence": 0.74,
            "reason": "This sounds like a building/neighbourhood coordination task where local help may be fastest. Why not other routes: DIY may not be allowed/safe; UC category may not fit building-level issues; waiting may delay resolution.",
            "clarifying_questions": [],
            "used_public_reference": False,
            "tool_trace": rec,
        }
        log_tool_trace(rec)
        return result

    if cat and cat_conf >= 0.6:
        ref = load_public_reference()
        ref_row = ref[ref["need"].str.lower().str.contains(cat.split()[0].lower(), na=False)].head(1)
        basis = str(ref_row.iloc[0]["public_basis"]) if not ref_row.empty else "Public guidance suggests evaluating the issue based on symptoms and timing."
        src = str(ref_row.iloc[0]["source_url"]) if not ref_row.empty else "https://www.cdc.gov/hygiene/about/cleaning-and-disinfecting-your-home.html"
        rec = _log_record("public_reference_lookup", f"Matched core category {cat}", t, "UC_CATEGORY", cat_conf, session_hash=session_hash)
        result = {
            "route": "UC_CATEGORY",
            "confidence": cat_conf,
            "reason": f"This maps to {cat}. Public context: {basis} Why not other routes: DIY may miss root cause if symptoms persist; local help may be fine but quality/fit varies; waiting may worsen the issue.",
            "clarifying_questions": [],
            "used_public_reference": True,
            "public_reference": {"category": cat, "basis": basis, "source_url": src},
            "category_info": f"{cat} is a relevant service category. Review public guidance and your own context before deciding. No in-app action is taken here.",
            "tool_trace": rec,
        }
        log_tool_trace(rec)
        return result

    rec = _log_record("ask_clarifying_question", "Insufficient confidence for a specific route", t, "WAIT_AND_WATCH", 0.45, session_hash=session_hash)
    result = {
        "route": "WAIT_AND_WATCH",
        "confidence": 0.45,
        "reason": "I don't have enough signal to recommend a specific route yet. Monitor for 24-48 hours and collect details. Why not other routes: DIY could be unsafe, local/UC routing could be mismatched without clearer symptoms.",
        "clarifying_questions": [
            "Is there any safety risk (smell, sparks, flooding, smoke)?",
            "What changed recently, and where exactly is the issue?",
        ],
        "used_public_reference": False,
        "tool_trace": rec,
    }
    log_tool_trace(rec)
    return result


def reflect(post_service_text: str, session_hash: str = "") -> dict[str, Any]:
    """Capture post-service reflection without PII or account actions."""
    t = str(post_service_text or "").strip()
    topics = []
    lower = t.lower()
    if any(w in lower for w in ["ac", "cooling"]):
        topics.append("AC maintenance timing")
    if any(w in lower for w in ["clean", "dust"]):
        topics.append("Cleaning cadence")
    if any(w in lower for w in ["leak", "tap", "plumb"]):
        topics.append("Plumbing check")
    if any(w in lower for w in ["pest", "cockroach", "ant"]):
        topics.append("Pest prevention")
    if not topics:
        topics.append("General home upkeep check")
    rec = _log_record("capture_reflection", "Captured post-service reflection", t, "REFLECTION", 0.7, session_hash=session_hash)
    log_tool_trace(rec)
    return {
        "open_topics": topics[:4],
        "unmet_expectation": any(w in lower for w in ["unclear", "didn't know", "not sure", "missing"]),
        "followup_question": "What home need might come up next in the next 30-90 days, based on what you noticed today?",
        "tool_trace": rec,
    }


def log_tool_trace(record: dict[str, Any]) -> None:
    config.ensure_dirs()
    rec = dict(record)
    rec.setdefault("ts", datetime.now(timezone.utc).isoformat())
    with config.TOOL_TRACE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def log_feedback(record: dict[str, Any]) -> None:
    config.ensure_dirs()
    rec = dict(record)
    rec.setdefault("ts", datetime.now(timezone.utc).isoformat())
    with config.MVP_FEEDBACK.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    demo_profile = {
        "city_tier": "Metro",
        "home_type": "Apartment",
        "household": ["Family"],
        "categories_used_before": ["AC Service"],
        "months_since_last_service": "2-3",
        "planning_style": "Reactive",
    }
    cal = build_calendar(demo_profile)
    print("Calendar items:", len(cal))
    for q in ["AC not cooling", "tap dripping", "something feels off in my kitchen but not sure what"]:
        r = route_need(q, demo_profile)
        print("---")
        print(q)
        print(r["route"], r["confidence"])
        print(r["reason"])
        print("clarifying:", r["clarifying_questions"])