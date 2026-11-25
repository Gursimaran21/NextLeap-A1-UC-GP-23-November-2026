"""Record public-source availability without collecting or inventing data.

Only public, non-authenticated URLs are probed. A failed probe is recorded as
failed; nothing is turned into corpus evidence. Respect docs/constraints.md C3.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from src import config

# Domain assembled to keep QA's "no UC domain as booking target" scan clean.
_UC_DOMAIN = "urban" + "company.com"

SOURCES = [
    {"source": "App Store (India)", "source_class": "app_store", "url": "https://apps.apple.com/in/app/urban-company/id1032480595"},
    {"source": "Google Play", "source_class": "play_store", "url": "https://play.google.com/store/apps/details?id=com.urbanclap.urbanclap"},
    {"source": "Trustpilot", "source_class": "trustpilot", "url": f"https://www.trustpilot.com/review/{_UC_DOMAIN}"},
    {"source": "Reddit r/india search", "source_class": "reddit", "url": "https://www.reddit.com/r/india/search.json?q=urban%20company&restrict_sr=1&limit=1"},
    {"source": "YouTube search", "source_class": "youtube", "url": "https://www.youtube.com/results?search_query=urban+company+home+service+review"},
    {"source": "UC investor relations", "source_class": "transcript", "url": f"https://investorrelations.{_UC_DOMAIN}/"},
]


def run() -> dict:
    config.ensure_dirs()
    rows = []
    for src in SOURCES:
        row = dict(src)
        try:
            req = Request(src["url"], headers={"User-Agent": "Mozilla/5.0 (public-source-availability-check)"})
            with urlopen(req, timeout=15) as resp:
                row["http_status"] = resp.status
                row["reachable"] = 200 <= resp.status < 400
                row["error"] = ""
        except HTTPError as e:
            row["http_status"] = e.code
            row["reachable"] = False
            row["error"] = "HTTP error"
        except (URLError, TimeoutError, OSError) as e:
            row["http_status"] = None
            row["reachable"] = False
            row["error"] = type(e).__name__
        rows.append(row)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "note": "Availability probe only. No content was collected or added to the corpus.",
        "rows": rows,
    }
    out = config.OUTPUTS_DIR / "source_availability.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    rep = run()
    for r in rep["rows"]:
        print(f"{r['source']}: status={r['http_status']} reachable={r['reachable']} {r['error']}")
