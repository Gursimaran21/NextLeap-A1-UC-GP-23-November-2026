"""Collect REAL public App Store reviews for Urban Company (India storefront).

Source: Apple's public customer-reviews RSS/JSON endpoint (no login, no UC scraping).
Respect docs/constraints.md (C3: public sources only; provenance recorded).

Usage:
    python -m scripts.collect_appstore            # pages 1-10, writes corpus
    python -m scripts.collect_appstore --pages 6

Outputs:
    data/raw/appstore_reviews.json   (raw records, gitignored)
    data/public_corpus.csv           (corpus rows with provenance)
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import config  # noqa: E402

APP_ID = "1032480595"  # Urban Company: Home Services (India App Store)
COUNTRY = "in"
SOURCE_NAME = "App Store (India)"
SOURCE_CLASS = "app_store"
APP_URL = f"https://apps.apple.com/{COUNTRY}/app/urban-company-home-services/id{APP_ID}?see-all=reviews"
UA = "Mozilla/5.0 (compatible; NextLeap-public-research/1.0)"


def fetch_page(page: int) -> list[dict]:
    url = (
        f"https://itunes.apple.com/{COUNTRY}/rss/customerreviews/"
        f"page={page}/id={APP_ID}/sortby=mostrecent/json"
    )
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    entries = (data.get("feed") or {}).get("entry") or []
    records = []
    for e in entries:
        if not isinstance(e, dict) or "im:rating" not in e:
            continue  # first entry can be app metadata
        records.append(
            {
                "review_id": (e.get("id") or {}).get("label", ""),
                "rating": (e.get("im:rating") or {}).get("label", ""),
                "title": (e.get("title") or {}).get("label", ""),
                "text": (e.get("content") or {}).get("label", ""),
                "review_date": ((e.get("updated") or {}).get("label", ""))[:10],
                "page_url": url,
            }
        )
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect public App Store reviews (C3-safe).")
    parser.add_argument("--pages", type=int, default=10, help="number of RSS pages (50 reviews each, max 10)")
    args = parser.parse_args()

    config.ensure_dirs()
    raw_dir = config.DATA_DIR / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    all_records: dict[str, dict] = {}
    for page in range(1, min(args.pages, 10) + 1):
        try:
            recs = fetch_page(page)
        except Exception as exc:  # noqa: BLE001
            print(f"page {page}: FAILED ({exc})")
            continue
        for r in recs:
            if r["review_id"]:
                all_records[r["review_id"]] = r
        print(f"page {page}: {len(recs)} reviews (total unique: {len(all_records)})")
        time.sleep(1.0)  # be polite to the public endpoint

    if not all_records:
        print("No reviews collected; aborting without touching the corpus.")
        sys.exit(1)

    raw_path = raw_dir / "appstore_reviews.json"
    raw_path.write_text(json.dumps(list(all_records.values()), ensure_ascii=False, indent=1), encoding="utf-8")

    today = date.today().isoformat()
    rows = []
    for rid, r in all_records.items():
        title = r["title"].strip()
        text = r["text"].strip()
        full = f"{title}. {text}" if title and title.lower() not in text.lower()[:60] else text
        rows.append(
            {
                "item_id": f"AS_{rid}",
                "source": SOURCE_NAME,
                "source_class": SOURCE_CLASS,
                "source_url": APP_URL,
                "access_date": today,
                "text": full,
                "rating": r["rating"],
                "city": "",
                "category": "",
                "return_signal_hint": "",
                "is_illustrative": False,
            }
        )

    df = pd.DataFrame(rows)
    df.to_csv(config.CORPUS, index=False)
    print(f"\nSaved {len(df)} REAL public reviews -> {config.CORPUS}")
    print(f"Raw records -> {raw_path}")
    print("Next: python -m src.engine  (then regenerate golden template + evidence log)")


if __name__ == "__main__":
    main()
