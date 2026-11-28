"""Home Care Companion MVP logic.

Deterministic-first, LLM-enhanced when available. No account actions, no messaging,
no service transactions. Respect docs/constraints.md (C1, C2, C3).
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date, datetime, timedelta, timezone
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

HISTORY_TIMING_OPTIONS = [
    "Not sure",
    "Never",
    "0-3 months",
    "4-6 months",
    "7-12 months",
    "12+ months",
]

TIMING_DAYS = {
    "0-3 months": 90,
    "4-6 months": 150,
    "7-12 months": 270,
    "12+ months": 400,
}

PLUMBING_ISSUE_OPTIONS = ["None", "Minor leak", "Major issue", "Not sure"]

NO_NEED_OPTIONS = [
    "AC servicing",
    "Deep home cleaning",
    "Pest control inspection",
    "Plumbing leak check",
]

HISTORY_TO_NEED = {
    "last_ac_service": "AC servicing",
    "last_deep_clean": "Deep home cleaning",
    "last_pest_control": "Pest control inspection",
    "last_plumbing_check": "Plumbing leak check",
}

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
        "id": "last_completed_service",
        "question": "Which is your last completed service?",
        "type": "single",
        "options": ["Not sure"] + config.CORE_CATEGORIES + ["Other"],
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

ROUTES = ["DIY", "LOCAL_OR_NEIGHBOUR", "UC_CATEGORY", "WAIT_AND_WATCH", "SEEK_IMMEDIATE_HELP", "NO_ACTION"]
TOOLS = [
    "ask_clarifying_question",
    "public_reference_lookup",
    "build_calendar",
    "route_need",
    "capture_reflection",
    "show_public_info",
    "summarise_plan",
]

URGENT_RE = re.compile(
    r"gas\s+smell|smell(?:s|ing)?\s+(?:of\s+)?gas|gas\s+leak|leaking\s+gas|"
    r"sparks?|sparking|burning\s+smell|smell\s+of\s+burning|"
    r"flooding|flooded|burst(?:ing)?\s+pipe|pipe\s+burst|water\s+everywhere|"
    r"electric\s+shock|fire",
    re.I,
)
DIY_RE = re.compile(r"filter|wipe|clean vent|tighten|unclog|drain hair|battery|remote|dust", re.I)
LOCAL_RE = re.compile(r"society|building electrician|neighbor|neighbour|watchman|caretaker|whatsapp group|local electrician from downstairs", re.I)
NO_NEED_RE = re.compile(
    r"\b(no need|nothing needed|don't need|do not need|not needed|no service needed|nothing to schedule)\b",
    re.I,
)

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
    reference_columns = [
        "need", "trigger", "typical_timing_days", "public_basis", "source_url",
        "source_class", "freshness", "match_strength",
    ]
    if not ref_path.exists():
        return pd.DataFrame(columns=reference_columns)
    df = pd.read_csv(ref_path)
    for col in reference_columns:
        if col not in df.columns:
            df[col] = ""
    df = df.fillna("")
    return df


def _safe_int(value: Any, default: int = 90) -> int:
    try:
        return int(float(value))
    except Exception:
        return default


def category_guide() -> list[dict[str, str]]:
    """Plain-language guide to the home-service categories in scope."""
    return [
        {
            "category": "AC Service",
            "covers": "Cooling performance, servicing and filter care",
            "consider_when": "Reduced cooling, dusty airflow, or before peak summer",
            "source_url": "https://www.energy.gov/energysaver/maintaining-your-air-conditioner",
        },
        {
            "category": "Deep Cleaning",
            "covers": "Whole-home refresh, soft furnishings and routine dust build-up",
            "consider_when": "Seasonal reset, festivals, or allergy symptoms",
            "source_url": "https://www.cdc.gov/hygiene/about/cleaning-and-disinfecting-your-home.html",
        },
        {
            "category": "Plumbing",
            "covers": "Leaks, taps, drains and water-pressure concerns",
            "consider_when": "Dampness, slow drainage, or unusual water use",
            "source_url": "https://www.epa.gov/watersense/fix-leak-week",
        },
        {
            "category": "Pest Control",
            "covers": "Inspection and prevention for common household pests",
            "consider_when": "Humid months, visible insects, or recurring sightings",
            "source_url": "https://www.cdc.gov/pests/index.html",
        },
        {
            "category": "Appliance Repair",
            "covers": "Fridge, washing machine, geyser and kitchen ventilation",
            "consider_when": "Unusual noise, weak performance, or safety signs",
            "source_url": "https://www.cpsc.gov/safety-education/safety-guides/home/electrical-safety",
        },
        {
            "category": "Salon",
            "covers": "At-home grooming and personal care",
            "consider_when": "A pre-planned grooming need or personal preference",
            "source_url": "",
        },
    ]


def build_plan_from_history(
    profile: dict[str, Any],
    history: dict[str, Any],
    reference: pd.DataFrame | None = None,
    llm: Any = None,
) -> list[dict[str, Any]]:
    """Build planning cues from customer-provided history plus public guidance.

    No item is a requirement: every cue carries its basis, confidence and source.
    """
    ref = reference if reference is not None else load_public_reference()
    history = dict(history or {})
    profile = dict(profile or {})
    no_need = {str(x).strip() for x in history.get("no_need_now", []) if str(x).strip()}
    items: list[dict[str, Any]] = []

    for field, need in HISTORY_TO_NEED.items():
        timing = str(history.get(field, "Not sure") or "Not sure").strip()
        if timing == "Never":
            continue

        match = ref[ref["need"].str.lower() == need.lower()]
        if match.empty:
            match = ref[ref["need"].str.lower().str.contains(need.split()[0].lower(), na=False)]

        basis = str(match.iloc[0]["public_basis"]) if not match.empty else "Public timing guidance is unavailable for this need."
        src = str(match.iloc[0]["source_url"]) if not match.empty else ""
        cadence = _safe_int(match.iloc[0]["typical_timing_days"], 90) if not match.empty else 90

        if need in no_need:
            items.append({
                "need": need,
                "status": "Not needed",
                "due_in_days": None,
                "why": "You marked this as not needed right now.",
                "basis": "Your own input.",
                "source_url": "",
                "confidence": 1.0,
                "route_hint": "NO_ACTION",
                "evidence": "customer input only",
                "cadence": cadence,
            })
            continue

        if timing not in TIMING_DAYS:
            items.append({
                "need": need,
                "status": "Needs more detail",
                "due_in_days": None,
                "why": "Timing was not provided, so no timing claim is made.",
                "basis": basis,
                "source_url": src,
                "confidence": 0.35,
                "route_hint": _route_hint_for_need(need),
                "evidence": "public guidance only; customer timing missing",
                "cadence": cadence,
            })
            continue

        days_until = cadence - TIMING_DAYS[timing]
        status = "Due now" if days_until <= 0 else ("Soon" if days_until <= 45 else "Later")
        items.append({
            "need": need,
            "status": status,
            "due_in_days": max(0, days_until),
            "why": f"Your last timing: {timing}. Public guidance suggests roughly {cadence} days between checks.",
            "basis": basis,
            "source_url": src,
            "confidence": 0.82 if timing in ("0-3 months", "4-6 months") else 0.72,
            "route_hint": _route_hint_for_need(need),
            "evidence": "customer timing + public guidance",
            "cadence": cadence,
        })

    issue = str(history.get("plumbing_issue", "None") or "None").strip()
    plumbing_row = ref[ref["need"].str.lower() == "plumbing leak check"]
    plumbing_src = str(plumbing_row.iloc[0]["source_url"]) if not plumbing_row.empty else "https://www.epa.gov/watersense/fix-leak-week"
    if issue == "None":
        items.append({
            "need": "Plumbing check",
            "status": "Not needed",
            "due_in_days": None,
            "why": "You reported no active plumbing issue.",
            "basis": "Your own input.",
            "source_url": "",
            "confidence": 1.0,
            "route_hint": "NO_ACTION",
            "evidence": "customer input only",
            "cadence": 60,
        })
    elif issue == "Minor leak":
        items.append({
            "need": "Plumbing leak check",
            "status": "Soon",
            "due_in_days": 7,
            "why": "You reported a minor leak; a timely check may help avoid waste or damage.",
            "basis": "Small leaks can waste water and cause damage if not addressed early.",
            "source_url": plumbing_src,
            "confidence": 0.65,
            "route_hint": "UC_CATEGORY_OR_LOCAL",
            "evidence": "customer note + public guidance",
            "cadence": 60,
        })
    elif issue == "Major issue":
        items.append({
            "need": "Qualified assessment for active issue",
            "status": "Needs attention",
            "due_in_days": 0,
            "why": "You reported a major issue. If there is flooding or electrical risk, seek qualified help first.",
            "basis": "Warning signs should be inspected by a qualified professional.",
            "source_url": "https://www.cpsc.gov/safety-education/safety-guides/home/electrical-safety",
            "confidence": 0.8,
            "route_hint": "SEEK_IMMEDIATE_HELP",
            "evidence": "customer note + public safety guidance",
            "cadence": 7,
        })
    else:
        items.append({
            "need": "Plumbing check",
            "status": "Needs more detail",
            "due_in_days": None,
            "why": "You were not sure about a plumbing issue, so no timing claim is made.",
            "basis": "Public guidance suggests checking unexpected dampness or higher water use.",
            "source_url": plumbing_src,
            "confidence": 0.4,
            "route_hint": "WAIT_AND_WATCH",
            "evidence": "public guidance only; customer detail missing",
            "cadence": 60,
        })

    upcoming = str(history.get("upcoming_need", "") or "").strip()
    if upcoming:
        items.append({
            "need": upcoming,
            "status": "Your note",
            "due_in_days": 30,
            "why": "You added this as an upcoming requirement.",
            "basis": "Your own note; no external claim is made.",
            "source_url": "",
            "confidence": 0.4,
            "route_hint": "USER_NOTE",
            "evidence": "customer input only",
            "cadence": 90,
        })

    if not items:
        items.append({
            "need": "No planning cues yet",
            "status": "Not needed",
            "due_in_days": None,
            "why": "No timing or needs were provided.",
            "basis": "Add optional history details if you want a planning cue.",
            "source_url": "",
            "confidence": 1.0,
            "route_hint": "NO_ACTION",
            "evidence": "no input provided",
            "cadence": 90,
        })

    items.sort(
        key=lambda x: (
            x.get("status") == "Not needed",
            x.get("due_in_days") if x.get("due_in_days") is not None else 999,
        )
    )
    for item in items:
        item.pop("cadence", None)
    return items


def _ics_escape(text: str) -> str:
    return (
        str(text or "")
        .replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
    )


def plan_to_ics(plan: list[dict[str, Any]]) -> str:
    """Create a private calendar file with one-day-before reminders."""
    today = date.today()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Urban Company Home Care Companion//Planning Cues//EN",
        "CALSCALE:GREGORIAN",
    ]
    added = 0
    for idx, item in enumerate(plan, start=1):
        if item.get("status") == "Not needed":
            continue
        due = _safe_int(item.get("due_in_days"), 90)
        event_date = today + timedelta(days=max(0, due))
        need = _ics_escape(item.get("need", "Home-care cue"))
        why = _ics_escape(item.get("why", ""))
        lines.extend([
            "BEGIN:VEVENT",
            f"UID:hcc-{stamp}-{idx}@local",
            f"DTSTAMP:{stamp}",
            f"DTSTART;VALUE=DATE:{event_date:%Y%m%d}",
            f"SUMMARY:{need} - planning cue",
            f"DESCRIPTION:{why}",
            "BEGIN:VALARM",
            "TRIGGER:-P1D",
            "ACTION:DISPLAY",
            f"DESCRIPTION:{need} planning reminder",
            "END:VALARM",
            "END:VEVENT",
        ])
        added += 1
    if added == 0:
        lines.extend([
            "BEGIN:VEVENT",
            f"UID:hcc-{stamp}-none@local",
            f"DTSTAMP:{stamp}",
            f"DTSTART;VALUE=DATE:{today:%Y%m%d}",
            "SUMMARY:No home-care planning cue selected",
            "DESCRIPTION:No reminder was added because no action is needed right now.",
            "END:VEVENT",
        ])
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


def plan_to_markdown(
    profile: dict[str, Any],
    history: dict[str, Any],
    plan: list[dict[str, Any]],
    summary: str = "",
) -> str:
    """Render the private plan as markdown for export."""
    lines = [
        "# Private Home-Care Plan",
        "",
        f"Generated locally on {date.today().isoformat()}. Planning cues only; no service is required by this plan.",
        "",
        "## Household context",
        "",
        f"- City tier: {profile.get('city_tier', 'Not provided')}",
        f"- Home type: {profile.get('home_type', 'Not provided')}",
        f"- Planning style: {profile.get('planning_style', 'Not provided')}",
        "",
        "## Service history you provided",
        "",
    ]
    for field, label in [
        ("last_ac_service", "Last AC servicing"),
        ("last_deep_clean", "Last deep cleaning"),
        ("last_pest_control", "Last pest control"),
        ("last_plumbing_check", "Last plumbing check"),
        ("plumbing_issue", "Plumbing issue"),
        ("upcoming_need", "Upcoming requirement"),
    ]:
        value = str((history or {}).get(field, "") or "Not provided").strip()
        lines.append(f"- {label}: {value}")
    lines.extend(["", "## Upcoming planning cues", ""])
    for item in plan:
        lines.append(f"- **{item.get('need', 'Cue')}** — {item.get('status', 'Unclear')}")
        lines.append(f"  - Why: {item.get('why', '')}")
        lines.append(f"  - Basis: {item.get('basis', '')} (confidence {item.get('confidence', 0):.2f})")
        if item.get("source_url"):
            lines.append(f"  - Source: {item['source_url']}")
    if summary:
        lines.extend(["", "## Plain-language summary", "", summary])
    lines.extend([
        "",
        "This file was created on your device. No account was accessed and no external action was taken.",
    ])
    return "\n".join(lines)


def summarise_plan(
    profile: dict[str, Any],
    history: dict[str, Any],
    plan: list[dict[str, Any]],
    llm: Any = None,
) -> str:
    """Grounded summary with a deterministic fallback."""
    names = ", ".join(str(p.get("need", "cue")) for p in plan) or "no planning cues"
    detail_gaps = sum(1 for p in plan if p.get("status") == "Needs more detail")
    not_needed = sum(1 for p in plan if p.get("status") == "Not needed")
    no_action_note = (
        f"{not_needed} item(s) are marked not needed and suggest no action. " if not_needed else ""
    )
    deterministic = (
        f"Your plan contains {len(plan)} planning cue(s): {names}. "
        f"{detail_gaps} item(s) need more detail before a timing cue can be shown. "
        f"{no_action_note}"
        "These are prompts to review your own home context, not proof that a service is necessary."
    )
    if llm is None or not hasattr(llm, "generate_json"):
        return deterministic

    payload = {
        "household_context": {
            "city_tier": profile.get("city_tier", ""),
            "home_type": profile.get("home_type", ""),
            "planning_style": profile.get("planning_style", ""),
        },
        "history": history,
        "plan_items": [
            {k: p.get(k) for k in ("need", "status", "why", "basis", "confidence", "source_url")}
            for p in plan
        ],
    }
    system = (
        "You summarise a home-care planning plan. Use only the supplied fields. "
        "Call items planning cues, never requirements. If timing is missing, say so. "
        "Do not suggest scheduling, messaging, account actions, or any transaction. "
        "Return one short paragraph in plain English."
    )
    prompt = f"Summarise this plan accurately:\n{json.dumps(payload, ensure_ascii=False)}"
    generated = llm.generate(system, prompt, temperature=0.2)
    if generated and len(generated.strip()) > 20:
        return generated.strip()
    return deterministic


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

    if NO_NEED_RE.search(t_lower):
        rec = _log_record("route_need", "User explicitly reported no need", t, "NO_ACTION", 0.95, session_hash=session_hash)
        result = {
            "route": "NO_ACTION",
            "confidence": 0.95,
            "reason": "Understood. No cue, reminder, or recommendation will be added for this request.",
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