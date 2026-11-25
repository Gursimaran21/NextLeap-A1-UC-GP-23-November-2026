"""Corpus ingestion, validation, provenance checks, and PII redaction.

Respect docs/constraints.md (C3, C7).
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd

from . import config
from .pii import contains_pii, redact_pii_counted

REQUIRED_COLUMNS = {"item_id", "source", "source_url", "text"}
DATE_COLUMNS = ("access_date", "date")
OPTIONAL_COLUMNS = {
    "source_class",
    "access_date",
    "date",
    "rating",
    "city",
    "category",
    "household_type",
    "first_found_uc",
    "return_signal_hint",
    "hint_return_signal",
    "is_illustrative",
}
PRIVATE_UC_PATH_MARKERS = (
    "/account",
    "/orders",
    "/bookings",
    "/profile",
    "/login",
    "/signin",
    "/checkout",
    "/payment",
    "/inbox",
    "/chat",
    "/app/",
)


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(c).strip().lower() for c in out.columns]
    # Harmonize schema variants.
    if "date" in out.columns and "access_date" not in out.columns:
        out["access_date"] = out["date"]
    if "hint_return_signal" in out.columns and "return_signal_hint" not in out.columns:
        out["return_signal_hint"] = out["hint_return_signal"]
    if "source_class" not in out.columns:
        out["source_class"] = "other"
    if "is_illustrative" not in out.columns:
        out["is_illustrative"] = False
    # Segmentation fields are optional; blank means "not captured" and is
    # reported as such by the engine instead of being silently dropped.
    for col in ("city", "category", "household_type", "first_found_uc"):
        if col not in out.columns:
            out[col] = ""
    return out


def _validate_required(df: pd.DataFrame) -> None:
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if not any(c in df.columns for c in DATE_COLUMNS):
        raise ValueError("Missing required date column: one of access_date/date")


def _validate_public_source(url: str) -> None:
    raw = str(url or "").strip()
    if not raw:
        raise ValueError("Empty source_url is not allowed (C3 provenance).")
    parsed = urlparse(raw)
    domain = (parsed.netloc or "").lower()
    path = (parsed.path or "").lower()
    if "urbancompany.com" in domain:
        if any(marker in path for marker in PRIVATE_UC_PATH_MARKERS):
            raise ValueError(f"Potential logged-in/app UC URL blocked by C3: {raw}")


def _coerce_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def load_corpus(path: str | Path | None = None) -> pd.DataFrame:
    """Load and validate the public corpus CSV.

    Redacts PII before any downstream use. Raises on C3/private UC URLs.
    """
    config.ensure_dirs()
    csv_path = Path(path) if path else config.CORPUS
    if not csv_path.exists():
        raise FileNotFoundError(f"Corpus not found: {csv_path}")

    df = pd.read_csv(csv_path)
    if df.empty:
        df.attrs.update(
            {
                "rows_loaded": 0,
                "redactions": 0,
                "sources_count": 0,
                "min_date": None,
                "max_date": None,
                "source_file": str(csv_path),
            }
        )
        return df

    df = _normalize_columns(df)
    _validate_required(df)

    df["source"] = df["source"].astype(str).str.strip()
    df["source_url"] = df["source_url"].astype(str).str.strip()
    df["text"] = df["text"].fillna("").astype(str)
    df["item_id"] = df["item_id"].astype(str).str.strip()
    df["source_class"] = df["source_class"].fillna("other").astype(str).str.strip().str.lower()
    df["is_illustrative"] = df["is_illustrative"].map(_coerce_bool)

    # C3 provenance checks.
    if (df["source"] == "").any() or (df["source_url"] == "").any():
        raise ValueError("Every row must have non-empty source and source_url (C3).")
    for url in df["source_url"].tolist():
        _validate_public_source(url)

    rows_loaded = len(df)
    redactions = 0
    cleaned_texts: list[str] = []
    for text in df["text"].tolist():
        cleaned, n = redact_pii_counted(text)
        redactions += n
        cleaned_texts.append(cleaned)
    df["text"] = cleaned_texts

    # Drop short/empty after redaction, then dedupe by cleaned text.
    df = df[df["text"].str.strip().str.len() >= 20].copy()
    df = df.drop_duplicates(subset=["text"]).reset_index(drop=True)

    # Final C7 safety gate.
    if df["text"].map(contains_pii).any():
        raise AssertionError("PII remains after redaction; ingestion blocked.")

    # Date metadata
    date_col = "access_date" if "access_date" in df.columns else "date"
    parsed_dates = pd.to_datetime(df[date_col], errors="coerce")
    min_date = parsed_dates.min()
    max_date = parsed_dates.max()

    df.attrs.update(
        {
            "rows_loaded": rows_loaded,
            "redactions": redactions,
            "sources_count": int(df["source"].nunique()) if not df.empty else 0,
            "min_date": None if pd.isna(min_date) else str(min_date.date()),
            "max_date": None if pd.isna(max_date) else str(max_date.date()),
            "source_file": str(csv_path),
        }
    )
    return df


def paste_corpus(text_block: str, source: str, source_url: str, source_class: str = "other") -> pd.DataFrame:
    """Create a small corpus DataFrame from pasted public text.

    Each non-empty line becomes one item. Intended for the Streamlit UI.
    """
    lines = [ln.strip() for ln in str(text_block or "").splitlines() if ln.strip()]
    now = datetime.now(timezone.utc).date().isoformat()
    rows = []
    for i, line in enumerate(lines, start=1):
        rows.append(
            {
                "item_id": f"PASTE_{i:03d}",
                "source": source.strip(),
                "source_class": source_class.strip().lower() or "other",
                "source_url": source_url.strip(),
                "access_date": now,
                "text": line,
                "rating": "",
                "city": "",
                "category": "",
                "household_type": "",
                "first_found_uc": "",
                "return_signal_hint": "unclear",
                "is_illustrative": False,
            }
        )
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    # Reuse validation/redaction path by writing to a temp-less in-memory flow.
    config.ensure_dirs()
    tmp = config.OUTPUTS_DIR / "_pasted_corpus_tmp.csv"
    df.to_csv(tmp, index=False)
    try:
        return load_corpus(tmp)
    finally:
        if tmp.exists():
            tmp.unlink()


def build_sample_corpus(path: str | Path | None = None, write: bool = True) -> pd.DataFrame:
    """Build a clearly-labelled ILLUSTRATIVE 40-row sample corpus.

    Used only when real public corpus is empty. Never pass off as real collected evidence.
    """
    config.ensure_dirs()
    out_path = Path(path) if path else (config.DATA_DIR / "public_corpus_sample.csv")
    today = datetime.now(timezone.utc).date().isoformat()

    def rows(source, source_class, base_url, items, start_idx):
        data = []
        for i, (text, category, signal) in enumerate(items, start=start_idx):
            data.append(
                {
                    "item_id": f"S{i:03d}",
                    "source": source,
                    "source_class": source_class,
                    "source_url": base_url,
                    "access_date": today,
                    "text": f"[ILLUSTRATIVE] {text}",
                    "rating": "",
                    "city": "Metro",
                    "category": category,
                    "return_signal_hint": signal,
                    "is_illustrative": True,
                }
            )
        return data

    sample: list[dict[str, object]] = []
    sample += rows(
        "App Store",
        "app_store",
        "https://apps.apple.com/in/app/urban-company/id1032480595",
        [
            ("Booked deep cleaning, it went fine but I never thought about what to book next.", "Deep Cleaning", "did_not_return"),
            ("AC service was good. Months later my tap leaked and I called a local plumber from WhatsApp.", "AC Service", "did_not_return"),
            ("I used salon at home once and forgot the app existed until a friend mentioned it.", "Salon", "did_not_return"),
            ("The cleaning was okay, but I didn't know they also do pest control.", "Deep Cleaning", "unclear"),
            ("After the service I had no idea when I should book again for maintenance.", "AC Service", "did_not_return"),
            ("Great job, I booked bathroom cleaning again two months later.", "Deep Cleaning", "returned"),
            ("Service was completed but there was no follow-up or reminder for next steps.", "Plumbing", "did_not_return"),
        ],
        1,
    )
    sample += rows(
        "Play Store",
        "play_store",
        "https://play.google.com/store/apps/details?id=com.urbanclap.urbanclap",
        [
            ("Used UC for AC repair once. Next time I needed electrician, I asked in my society group.", "AC Service", "did_not_return"),
            ("The app is fine but I don't remember it when something breaks suddenly.", "Plumbing", "did_not_return"),
            ("I booked pest control and later booked cleaning because I saw it in the app.", "Pest Control", "returned"),
            ("Didn't know Urban Company had appliance repair too, used a local shop.", "Appliance Repair", "did_not_return"),
            ("After a good service I still wasn't sure what else my home needed.", "Deep Cleaning", "unclear"),
            ("I only use it when something goes wrong, never for planned upkeep.", "Plumbing", "did_not_return"),
            ("The professional was late and left a mess; I didn't want to try again.", "Deep Cleaning", "did_not_return"),
        ],
        8,
    )
    sample += rows(
        "Trustpilot",
        "trustpilot",
        "https://www.trustpilot.com/review/urbancompany.com",
        [
            ("Booking was smooth but I had no reason to open the app again for weeks.", "Salon", "did_not_return"),
            ("I got my sofa cleaned once; I didn't know the right frequency for booking again.", "Deep Cleaning", "unclear"),
            ("Bad experience with rescheduling made me avoid the app.", "AC Service", "did_not_return"),
            ("They refunded my booking after a poor visit, so I stopped using it.", "Plumbing", "did_not_return"),
            ("Service quality was fine, but my building handyman is just easier for small jobs.", "Plumbing", "did_not_return"),
            ("I came back for another service because I trusted the first professional.", "Salon", "returned"),
        ],
        15,
    )
    sample += rows(
        "Reddit",
        "reddit",
        "https://www.reddit.com/r/india/",
        [
            ("Used Urban Company once for deep cleaning before Diwali, then went back to local help.", "Deep Cleaning", "did_not_return"),
            ("I never know if I should call a professional or just DIY small repairs.", "Plumbing", "unclear"),
            ("For AC servicing I usually wait until summer and ask neighbours who they use.", "AC Service", "did_not_return"),
            ("UC is good for one-off jobs but I don't think of it as home maintenance.", "Deep Cleaning", "did_not_return"),
            ("I booked again because the app showed me another service I actually needed.", "Salon", "returned"),
            ("My parents prefer calling the same local person on WhatsApp every time.", "Plumbing", "did_not_return"),
            ("If the app reminded me before monsoon, I might have booked pest control there.", "Pest Control", "did_not_return"),
        ],
        21,
    )
    sample += rows(
        "YouTube comments",
        "youtube",
        "https://www.youtube.com/results?search_query=urban+company+home+service+review",
        [
            ("I tried them once and the service was decent, but I forgot about them later.", "Deep Cleaning", "did_not_return"),
            ("Good for AC service, but for small fixes my local electrician is faster.", "AC Service", "did_not_return"),
            ("Did not know they do so many categories until I watched this video.", "Appliance Repair", "unclear"),
            ("I only book when there is a big problem, not for regular maintenance.", "Plumbing", "did_not_return"),
            ("Had a warranty issue and the redo took too long.", "AC Service", "did_not_return"),
            ("Booked again after a good first experience, this time for cleaning.", "Salon", "returned"),
            ("I wish I knew when to service appliances before they break down.", "Appliance Repair", "unclear"),
        ],
        28,
    )
    sample += rows(
        "Earnings transcript",
        "transcript",
        "https://investorrelations.urbancompany.com/",
        [
            ("Management noted repeat customers contribute a large share of transaction value.", "All", "returned"),
            ("The company discussed improving customer retention and repeat behavior over time.", "All", "unclear"),
            ("Transcript highlighted category expansion as a way to serve more household needs.", "All", "unclear"),
            ("Management mentioned customers often use services for specific occasions rather than routines.", "All", "did_not_return"),
            ("The company discussed building trust and habit in home services.", "All", "unclear"),
            ("Retention was described as a strategic priority alongside service quality.", "All", "unclear"),
        ],
        35,
    )

    df = pd.DataFrame(sample[:40])
    if write:
        df.to_csv(out_path, index=False)
    return df


if __name__ == "__main__":
    config.ensure_dirs()
    sample_path = config.DATA_DIR / "public_corpus_sample.csv"
    if not sample_path.exists():
        build_sample_corpus(sample_path, write=True)
    df = load_corpus(sample_path)
    print(f"loaded {df.attrs.get('rows_loaded', len(df))} rows -> kept {len(df)}")
    print(f"sources={df.attrs.get('sources_count')} redactions={df.attrs.get('redactions')}")
    print(f"illustrative={bool(df['is_illustrative'].any()) if 'is_illustrative' in df.columns else False}")