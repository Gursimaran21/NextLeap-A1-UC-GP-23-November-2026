"""Central config and constants for the UC Graduation Project.

No secrets here - API keys come from environment/.env.
Respect docs/constraints.md.
"""

from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUTS_DIR = ROOT / "outputs"
DOCS_DIR = ROOT / "docs"

CORPUS = DATA_DIR / "public_corpus_merged.csv"  # App Store + Google Play; legacy App Store snapshot kept at public_corpus.csv
GOLDEN = DATA_DIR / "golden_set.csv"
INTERVIEWS = DATA_DIR / "interviews.csv"
REFERENCE = DATA_DIR / "public_reference.csv"

DISCOVERY_JSON = OUTPUTS_DIR / "discovery_results.json"
EVIDENCE_MD = OUTPUTS_DIR / "evidence_log.md"
EVIDENCE_PDF = OUTPUTS_DIR / "evidence_log.pdf"
DECK_PDF = OUTPUTS_DIR / "NL_UrbanCompany.pdf"
TOOL_TRACE = OUTPUTS_DIR / "tool_trace.jsonl"
MVP_FEEDBACK = OUTPUTS_DIR / "mvp_feedback.jsonl"


def ensure_dirs() -> None:
    """Create required project directories if they do not exist."""
    for path in (DATA_DIR, OUTPUTS_DIR, DOCS_DIR):
        path.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# METRIC CONSTANTS (C4/C5)
# ---------------------------------------------------------------------------
METRIC_NAME = "Share of customers who complete another booking within 90 days of a completed booking"
ANCHOR_MONTH = "2026-08"  # Chosen analysis month; document rationale in deck/docs.
WINDOW_DAYS = 90
EXCLUDED_CATEGORIES = ["InstaHelp", "instahelp", "quick-service housekeeping"]
EXCLUDED_OUTCOMES = ["redo", "warranty", "refund", "refunded"]
CORE_CATEGORIES = [
    "Deep Cleaning",
    "AC Service",
    "Plumbing",
    "Salon",
    "Pest Control",
    "Appliance Repair",
]
REPEAT_NTV_PCT = 84

METRIC_DEFINITION = """Business metric: Share of customers who complete another booking within 90 days of a completed booking.

Anchor booking: Pick a month. Every customer whose first completed booking in that month was in a core category is counted once. That booking is their anchor booking. Quick-service housekeeping (InstaHelp) is excluded.

Return / "books another service": Customer completes any later booking, in any category, within 90 days of the anchor booking.

Do not count: Redos, warranty claims, and bookings that end in a refund.

Business context: About 84% of Urban Company's net transaction value comes from repeat customers."""


# ---------------------------------------------------------------------------
# THEME LEGEND (exact codes)
# ---------------------------------------------------------------------------
THEMES: list[dict[str, object]] = [
    {
        "code": "T1_POST_SERVICE_CLOSURE",
        "name": "Post-service closure gap",
        "meaning": "After service, no clear next step/closure; need fades.",
        "keywords": ["what next", "after service", "no follow up", "forgot", "didn't think", "nothing else"],
        "control": False,
        "out_of_scope": False,
        "excluded_from_metric": False,
    },
    {
        "code": "T2_NEED_RECOGNITION",
        "name": "Need recognition gap",
        "meaning": "Customer doesn't recognize when next need arises.",
        "keywords": ["didn't realize", "didn't notice", "didn't know when", "missed", "should have done"],
        "control": False,
        "out_of_scope": False,
        "excluded_from_metric": False,
    },
    {
        "code": "T3_MENTAL_AVAILABILITY",
        "name": "Mental availability gap",
        "meaning": "UC not top-of-mind when need arises.",
        "keywords": ["forgot about urban company", "didn't think of uc", "remembered later", "not top of mind"],
        "control": False,
        "out_of_scope": False,
        "excluded_from_metric": False,
    },
    {
        "code": "T4_CATEGORY_AWARENESS",
        "name": "Category awareness gap",
        "meaning": "Customer unaware UC offers needed category.",
        "keywords": ["didn't know uc does", "thought they only do", "didn't see category", "not aware"],
        "control": False,
        "out_of_scope": False,
        "excluded_from_metric": False,
    },
    {
        "code": "T5_LOCAL_WHATSAPP_DEFAULT",
        "name": "Local/WhatsApp default",
        "meaning": "Defaults to local provider/neighbour/WhatsApp/family.",
        "keywords": ["local guy", "neighbour", "neighbor", "whatsapp", "family recommended", "regular electrician", "society vendor"],
        "control": False,
        "out_of_scope": False,
        "excluded_from_metric": False,
    },
    {
        "code": "T6_DECISION_CONFIDENCE",
        "name": "Decision confidence gap",
        "meaning": "Unsure what service is needed / DIY vs professional.",
        "keywords": ["not sure", "do i need", "diy", "can i fix", "what service", "confused"],
        "control": False,
        "out_of_scope": False,
        "excluded_from_metric": False,
    },
    {
        "code": "T7_PLANNING_SEASONALITY",
        "name": "Planning/seasonality gap",
        "meaning": "Need is seasonal/planned but not anticipated.",
        "keywords": ["before summer", "monsoon", "festival", "seasonal", "every year", "due for"],
        "control": False,
        "out_of_scope": False,
        "excluded_from_metric": False,
    },
    {
        "code": "T8_EXPERIENCE_QUALITY",
        "name": "Experience/quality issue",
        "meaning": "Service quality/experience issue.",
        "keywords": ["bad service", "poor quality", "late", "rude", "damaged", "not clean", "unprofessional"],
        "control": True,
        "out_of_scope": False,
        "excluded_from_metric": False,
    },
    {
        "code": "T9_PRICE_OFFER",
        "name": "Price/offer expectation",
        "meaning": "Price/discount/incentive expectation.",
        "keywords": ["discount", "coupon", "expensive", "price", "offer", "cashback", "membership"],
        "control": True,
        "out_of_scope": True,
        "excluded_from_metric": False,
    },
    {
        "code": "T10_REDO_REFUND",
        "name": "Redo/refund/warranty",
        "meaning": "Redo/warranty/refund case.",
        "keywords": ["redo", "refund", "warranty", "complaint", "came back to fix"],
        "control": False,
        "out_of_scope": False,
        "excluded_from_metric": True,
    },
    {
        "code": "T11_UNCLASSIFIED",
        "name": "Unclassified",
        "meaning": "Insufficient signal.",
        "keywords": [],
        "control": False,
        "out_of_scope": False,
        "excluded_from_metric": False,
    },
]

THEME_BY_CODE: dict[str, dict[str, object]] = {t["code"]: t for t in THEMES}
THEME_CODES: list[str] = [str(t["code"]) for t in THEMES]

BIAS_FLAGS = ["bad_experience_overrepresented", "silent_nonreturner_proxy", "none"]
RETURN_SIGNALS = ["returned", "did_not_return", "unclear"]
SOURCE_CLASSES = [
    "app_store",
    "play_store",
    "trustpilot",
    "reddit",
    "youtube",
    "social",
    "transcript",
    "news",
    "forum",
    "other",
]


# ---------------------------------------------------------------------------
# SEGMENT
# ---------------------------------------------------------------------------
SEGMENT_NAME = "Urban renters/families in metros who used one core category once and then went quiet"
SEGMENT_NOTES: dict[str, object] = {
    "city_tier": "Metro / Tier 1 (hypothesis; validate in research)",
    "household": "Renters or families managing routine home maintenance",
    "categories_focus": ["Deep Cleaning", "AC Service", "Plumbing", "Salon"],
    "behavior": "Completed one core-category booking; did not complete another booking within 90 days",
    "excluded": ["InstaHelp/quick-service housekeeping", "redo/warranty/refund-only journeys"],
}


# ---------------------------------------------------------------------------
# DECOMPOSITION D1..D6
# ---------------------------------------------------------------------------
DECOMPOSITION: list[dict[str, object]] = [
    {
        "id": "D1",
        "stage": "Need incidence",
        "question": "Did another home-service need actually arise in the 90-day window?",
        "customer_can_answer": "Yes - can report what needs came up at home.",
        "public_proxy": "Seasonal/service cadence references in public discussions; not directly observable.",
        "influenceable": False,
        "publicly_measurable": False,
        "product_outcome": "Anticipate genuine needs without creating them",
        "measurable_indicator": "Public cadence/seasonality references (not directly observable)",
        "notes": "Mostly exogenous; product can anticipate but cannot create genuine need.",
    },
    {
        "id": "D2",
        "stage": "Need recognition",
        "question": "Did the customer recognize the need in time?",
        "customer_can_answer": "Yes - can describe when they noticed or missed it.",
        "public_proxy": "Posts/comments about forgotten maintenance, seasonal timing, or delayed repairs.",
        "influenceable": True,
        "publicly_measurable": False,
        "product_outcome": "Timely need recognition",
        "measurable_indicator": "Interview recall of missed or delayed maintenance",
        "notes": "Customer-side reminders/education can help without creating false need.",
    },
    {
        "id": "D3",
        "stage": "Mental availability",
        "question": "When the need arose, did they think of Urban Company?",
        "customer_can_answer": "Yes - recall/consideration questions in interview.",
        "public_proxy": "Mentions of alternatives used; limited direct signal.",
        "influenceable": True,
        "publicly_measurable": False,
        "product_outcome": "Post-service continuity / top-of-mind",
        "measurable_indicator": "Interview consideration and recall questions",
        "notes": "Post-service continuity can improve recall.",
    },
    {
        "id": "D4",
        "stage": "Category consideration",
        "question": "Did they know UC offered the relevant category/service?",
        "customer_can_answer": "Yes - awareness questions.",
        "public_proxy": "Reviews/comments asking whether UC does X.",
        "influenceable": True,
        "publicly_measurable": False,
        "product_outcome": "Category clarity",
        "measurable_indicator": "Interview awareness questions; public 'does UC do X?' posts",
        "notes": "Customer-side information can clarify category fit.",
    },
    {
        "id": "D5",
        "stage": "Choice vs alternatives",
        "question": "Did they choose UC over local/DIY/WhatsApp/family/neighbour options?",
        "customer_can_answer": "Yes - can describe alternatives considered.",
        "public_proxy": "Public posts comparing local vendors, WhatsApp groups, DIY.",
        "influenceable": True,
        "publicly_measurable": False,
        "product_outcome": "Confident choice vs alternatives",
        "measurable_indicator": "Interview alternatives used; public comparison posts",
        "notes": "Must respect C1: no discounts/incentives; influence via confidence/planning value.",
    },
    {
        "id": "D6",
        "stage": "Frictionless completion",
        "question": "If they chose UC, could they complete the booking without friction?",
        "customer_can_answer": "Yes - but this is closer to experience/ops; use carefully.",
        "public_proxy": "App reviews about booking/payment/support friction.",
        "influenceable": True,
        "publicly_measurable": False,
        "product_outcome": "Frictionless completion (customer-side clarity)",
        "measurable_indicator": "Public reviews about booking/payment/support friction",
        "notes": "Some parts are product/ops; keep solution customer-side and avoid bad-experience-only framing.",
    },
]


# ---------------------------------------------------------------------------
# PALETTE (colour-blind-safe; never red/green-only encoding)
# ---------------------------------------------------------------------------
PALETTE: dict[str, str] = {
    "ink": "#12212B",
    "teal": "#0B6E4F",
    "amber": "#E08A00",
    "blue": "#2C6EAA",
    "grey": "#6B7A83",
    "light": "#F3F6F5",
    "white": "#FFFFFF",
}


# ---------------------------------------------------------------------------
# LIMITS / QA CONSTANTS
# ---------------------------------------------------------------------------
GOLDEN_N = 20
INTERVIEW_MIN = 5
INTERVIEW_MAX = 6
DECK_MAX_SLIDES = 10
MIN_FONT_PT = 14
MAX_PDF_MB = 40
MIN_CORPUS = 150
FELLOW_NAME_TO_EXCLUDE = ""  # Set locally before final QA; do not commit personal name.
DECK_PDF_NAME = "NL_UrbanCompany.pdf"


# ---------------------------------------------------------------------------
# GUARDRAILS
# ---------------------------------------------------------------------------
FORBIDDEN_PATTERNS: list[str] = [
    "discount",
    "coupon",
    "promo code",
    "promo",
    "cashback",
    "membership",
    "free trial",
    "voucher",
    "referral bonus",
    "loyalty points",
    "price change",
    "lower price",
    "cheaper",
    "fee waiver",
    "professional pay",
    "partner earnings",
    "commission change",
    "incentive for professionals",
    "penalize professionals",
    "book now",
    "book again",
    "schedule now",
    "pay now",
    "checkout",
    "message professional",
    "contact pro",
    "cancel booking",
    "modify booking",
    "bad experience",
    "offer to come back",
]

ALLOWED_FRAMING_NOTE = (
    "Focus on customer-side planning, awareness, decision confidence, timing, and continuity."
)
