"""Research data helpers. Respect docs/constraints.md (C6, C7)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from . import config

REQUIRED_INTERVIEW_COLS = [
    "respondent_id",
    "interview_date",
    "consent",
    "city_tier",
    "household_type",
    "decision_maker",
    "last_booking_date",
    "category",
    "total_bookings",
    "anchor_booking_date",
    "returner_90d",
    "subsequent_need",
    "Q4_discovery",
    "Q5_booking_reason",
    "Q6_provider_choice",
    "Q7_post_service",
    "Q8_expectations",
    "Q9_next_need",
    "Q10_arrangement",
    "Q11_considered_UC",
    "Q12_alternative",
    "Q13_return_motivation",
    "Q14_barriers",
    "Q15_planning",
    "Q16_tracking_value",
    "Q17_decision_information",
    "Q18_usefulness",
    "main_barrier",
    "notes",
    "quote",
    "theme_code",
]
PII_LIKE_COLS = {
    "name", "full_name", "phone", "mobile", "email", "address", "flat",
    "flat_number", "screenshot", "invoice", "booking_screenshot", "photo",
    "contact", "whatsapp_number",
}
ALLOWED_RESPONDENTS = {f"R0{i}" for i in range(1, 7)}
ALLOWED_RETURNER = {"yes", "no"}


def load_interviews(path: str | Path | None = None) -> pd.DataFrame:
    """Load and validate anonymized interview data. Raises on PII-like columns or schema issues."""
    config.ensure_dirs()
    p = Path(path) if path else config.INTERVIEWS
    if not p.exists():
        return pd.DataFrame(columns=REQUIRED_INTERVIEW_COLS)
    df = pd.read_csv(p)
    cols = {c.strip() for c in df.columns}
    cols_lower = {c.strip().lower() for c in df.columns}

    bad = sorted(cols_lower.intersection(PII_LIKE_COLS))
    if bad:
        raise ValueError(f"PII-like columns not allowed in interviews: {bad}")

    missing = [c for c in REQUIRED_INTERVIEW_COLS if c not in cols]
    if missing:
        raise ValueError(f"Missing required interview columns: {missing}")

    # Strip stray whitespace while preserving the exact schema casing (e.g., Q4_discovery).
    rename = {c: c.strip() for c in df.columns}
    df = df.rename(columns=rename)

    df["respondent_id"] = df["respondent_id"].astype(str).str.strip().str.upper()
    bad_ids = sorted(set(df["respondent_id"]) - ALLOWED_RESPONDENTS - {"" , "NAN"})
    if bad_ids:
        raise ValueError(f"respondent_id must be R01..R06; got: {bad_ids}")

    df["returner_90d"] = df["returner_90d"].astype(str).str.strip().str.lower()
    bad_ret = sorted(set(df["returner_90d"]) - ALLOWED_RETURNER - {"", "nan"})
    if bad_ret:
        raise ValueError(f"returner_90d must be yes/no; got: {bad_ret}")

    df["total_bookings"] = pd.to_numeric(df["total_bookings"], errors="coerce").fillna(0).astype(int)
    if (df["total_bookings"] < 0).any():
        raise ValueError("total_bookings must be >= 0")

    return df


def interview_template() -> pd.DataFrame:
    """Return an empty anonymized interview template."""
    return pd.DataFrame([{
        "respondent_id": "R01",
        "interview_date": "",
        "consent": "",
        "city_tier": "",
        "household_type": "",
        "decision_maker": "",
        "last_booking_date": "",
        "category": "AC Service",
        "total_bookings": 1,
        "anchor_booking_date": "",
        "returner_90d": "no",
        "subsequent_need": "",
        "Q4_discovery": "",
        "Q5_booking_reason": "",
        "Q6_provider_choice": "",
        "Q7_post_service": "",
        "Q8_expectations": "",
        "Q9_next_need": "",
        "Q10_arrangement": "",
        "Q11_considered_UC": "",
        "Q12_alternative": "",
        "Q13_return_motivation": "",
        "Q14_barriers": "",
        "Q15_planning": "",
        "Q16_tracking_value": "",
        "Q17_decision_information": "",
        "Q18_usefulness": "",
        "main_barrier": "",
        "notes": "",
        "quote": "",
        "theme_code": "T1_POST_SERVICE_CLOSURE",
    }])