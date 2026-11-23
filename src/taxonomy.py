"""Theme taxonomy, coding guidance, and bias notes.

Respect docs/constraints.md.
"""

from __future__ import annotations

from . import config

THEME_DEFINITIONS: dict[str, dict[str, object]] = {
    "T1_POST_SERVICE_CLOSURE": {
        "name": "Post-service closure gap",
        "include": [
            "After service completion, customer has no clear next step",
            "Need fades because nothing carried the context forward",
            "Customer didn't think of what else to book after a good service",
        ],
        "exclude": [
            "Poor service quality complaints (T8)",
            "Explicit price/discount expectation (T9)",
        ],
    },
    "T2_NEED_RECOGNITION": {
        "name": "Need recognition gap",
        "include": [
            "Customer didn't recognize a home need in time",
            "Missed maintenance timing or noticed too late",
        ],
        "exclude": ["Knew the need but chose local alternative (T5)", "Knew need but forgot UC (T3)"],
    },
    "T3_MENTAL_AVAILABILITY": {
        "name": "Mental availability gap",
        "include": [
            "Customer forgot Urban Company when need arose",
            "UC not top-of-mind despite prior use",
        ],
        "exclude": ["Customer didn't know UC offered the category (T4)"],
    },
    "T4_CATEGORY_AWARENESS": {
        "name": "Category awareness gap",
        "include": [
            "Customer unaware UC offers the needed category/service",
            "Assumed UC only does certain categories",
        ],
        "exclude": ["Knew category existed but chose local provider (T5)"],
    },
    "T5_LOCAL_WHATSAPP_DEFAULT": {
        "name": "Local/WhatsApp default",
        "meaning": "Defaults to local provider/neighbour/WhatsApp/family.",
        "include": [
            "Used local handyman/vendor/society contact",
            "Asked neighbours/family/WhatsApp group",
            "Preferred familiar local person for convenience/trust",
        ],
        "exclude": ["Chose UC but had quality issue (T8)"],
    },
    "T6_DECISION_CONFIDENCE": {
        "name": "Decision confidence gap",
        "include": [
            "Unsure whether problem needs professional or DIY",
            "Unsure which service/category fits the problem",
        ],
        "exclude": ["Clear need but chose local provider (T5)"],
    },
    "T7_PLANNING_SEASONALITY": {
        "name": "Planning/seasonality gap",
        "include": [
            "Seasonal/periodic need not anticipated",
            "Before summer/monsoon/festival maintenance timing missed",
        ],
        "exclude": ["General forgetfulness unrelated to timing (T2/T3)"],
    },
    "T8_EXPERIENCE_QUALITY": {
        "name": "Experience/quality issue",
        "include": [
            "Poor service quality, late arrival, unprofessional behavior, damage, incomplete work",
            "Dirt left behind, bad cleaning, broken item, rude professional",
        ],
        "exclude": [
            "No next-step after a good service (T1)",
            "Price/discount complaints (T9)",
            "Redo/refund/warranty as metric exclusion case (T10) where appropriate",
        ],
    },
    "T9_PRICE_OFFER": {
        "name": "Price/offer expectation",
        "include": ["Discount/coupon/cashback/membership/price expectation as main reason"],
        "exclude": ["Non-price continuity gaps (T1-T7)"],
    },
    "T10_REDO_REFUND": {
        "name": "Redo/refund/warranty",
        "include": ["Redo, warranty claim, refund, or booking corrected after failure"],
        "exclude": ["General quality complaint without redo/refund (T8)"],
    },
    "T11_UNCLASSIFIED": {
        "name": "Unclassified",
        "include": ["Insufficient signal to assign a meaningful theme"],
        "exclude": ["Any clear T1-T10 signal"],
    },
}

RETURN_SIGNAL_RULES = {
    "returned": "Evidence indicates the customer booked again / returned / repeated use.",
    "did_not_return": "Evidence indicates customer did not return, used alternative, or went quiet.",
    "unclear": "No clear return signal in the text.",
}

SAMPLING_NOTES = [
    "Bad-experience over-representation: complaint-heavy sources (app stores, Trustpilot/forums) can over-weight T8/T10. Stratify by source and report continuity vs experience separately.",
    "Silent non-returners leave no trace: public text under-observes customers who simply never came back. Use interviews as corrective evidence and label silent_nonreturner_proxy when text suggests quiet drop-off.",
]

VALID_THEME_CODES = set(config.THEME_CODES)
COMPLAINT_HEAVY_SOURCES = {"app_store", "play_store", "trustpilot", "forum", "consumer_forum"}
CONTINUITY_THEMES = {"T1_POST_SERVICE_CLOSURE", "T2_NEED_RECOGNITION", "T3_MENTAL_AVAILABILITY", "T4_CATEGORY_AWARENESS", "T5_LOCAL_WHATSAPP_DEFAULT", "T6_DECISION_CONFIDENCE", "T7_PLANNING_SEASONALITY"}
EXPERIENCE_CONTROL_THEMES = {"T8_EXPERIENCE_QUALITY", "T9_PRICE_OFFER", "T10_REDO_REFUND"}


def theme_prompt_block() -> str:
    lines = []
    for code in config.THEME_CODES:
        d = THEME_DEFINITIONS[code]
        include = "; ".join(d.get("include", []))
        exclude = "; ".join(d.get("exclude", []))
        lines.append(f"- {code} ({d['name']}): INCLUDE: {include}. EXCLUDE: {exclude}.")
    return "\n".join(lines)
