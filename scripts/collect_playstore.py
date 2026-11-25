"""Collect public Google Play (India) reviews for Urban Company.

Public, unauthenticated source only. No logged-in pages, no app scraping.
Raw responses are saved with provenance; PII is removed later by src.ingest.
Respect docs/constraints.md (C3, C7).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pandas as pd
from google_play_scraper import Sort, reviews

from src import config

APP_ID = "com.urbanclap.urbanclap"
LISTING_URL = f"https://play.google.com/store/apps/details?id={APP_ID}"
TARGET_COUNT = 250


def collect(count: int = TARGET_COUNT) -> list[dict]:
    fetched, _ = reviews(
        APP_ID,
        lang="en",
        country="in",
        count=count,
        sort=Sort.NEWEST,
    )
    return [
        {
            "review_id": str(r.get("reviewId", "")),
            "text": str(r.get("content", "") or ""),
            "rating": r.get("score"),
            "at": str(r.get("at")) if r.get("at") is not None else "",
        }
        for r in fetched
    ]


def run() -> dict:
    config.ensure_dirs()
    today = datetime.now(timezone.utc).date().isoformat()
    raw = collect()
    raw_path = config.DATA_DIR / "raw" / "playstore_reviews.json"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_text(
        json.dumps({
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "app_id": APP_ID,
            "country": "in",
            "lang": "en",
            "source_url": LISTING_URL,
            "fetched": len(raw),
            "reviews": raw,
        }, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    if not raw:
        return {"fetched": 0, "added": 0, "raw": str(raw_path)}

    rows = []
    for r in raw:
        text = str(r["text"] or "").strip()
        if len(text) < 20:
            continue
        rid = "".join(ch for ch in r["review_id"] if ch.isalnum() or ch in "_-")[:60]
        rows.append({
            "item_id": f"GP_{rid}",
            "source": "Google Play",
            "source_class": "play_store",
            "source_url": LISTING_URL,
            "access_date": today,
            "text": text,
            "rating": r.get("rating", ""),
            "city": "",
            "category": "",
            "household_type": "",
            "first_found_uc": "",
            "return_signal_hint": "unclear",
            "is_illustrative": False,
        })

    new = pd.DataFrame(rows).drop_duplicates(subset=["text"])
    base_path = config.CORPUS if config.CORPUS.exists() else config.DATA_DIR / "public_corpus.csv"
    if base_path.exists():
        existing = pd.read_csv(base_path)
        before = len(existing)
        combined = pd.concat([existing, new], ignore_index=True)
        combined = combined.drop_duplicates(subset=["item_id"]).drop_duplicates(subset=["text"])
        added = len(combined) - before
    else:
        combined = new
        added = len(new)
    combined.to_csv(config.CORPUS, index=False)
    return {"fetched": len(raw), "added": added, "corpus_rows": len(combined), "raw": str(raw_path), "corpus": str(config.CORPUS)}


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2))
