# Sources & Data Access

Respect `docs/constraints.md` (C3). Public sources only. No logged-in Urban Company scraping.

| Source class | What we took | URL pattern / example | Public access confirmation | What we did NOT access |
|---|---|---|---|---|
| App Store reviews | Public review text, rating, date, geography/language if visible | https://apps.apple.com/* | Public page, no login | UC internal dashboards, private support tickets |
| Play Store reviews | Public review text, rating, date | https://play.google.com/store/apps/* | Public page, no login | Logged-in UC account data |
| Trustpilot/public review sites | Public review text, date, rating | https://www.trustpilot.com/* | Public page, no login | Private messages, account details |
| Reddit/forums | Public posts/comments about home services/UC | https://www.reddit.com/* | Public threads only | Private subreddits/DMs |
| YouTube/public transcripts | Publicly available transcript/comment text | https://www.youtube.com/* | Public video/transcript | Private/unlisted owner analytics |
| Public reference sources | Home-maintenance timing/cadence guidance | e.g. CDC/EPA/public home-care pages | Public | Paywalled or logged-in sources |
| Primary interviews | Anonymized notes/quotes (R01–R06) | N/A (offline collection) | Consent-based, anonymized | Names, phone, address, screenshots, invoices, personal docs |

## Actually collected (real, not illustrative)

| Date | Source | Method | Volume | Provenance |
|---|---|---|---|---|
| 2026-11-23 | App Store (India) — Urban Company app id `1032480595` | Apple public customer-reviews RSS/JSON (`itunes.apple.com/in/rss/customerreviews/...`), pages 1–10, no login | 500 fetched → 465 kept after ingest (PII redaction, <20-char drop, dedupe) | `source_url` = public App Store reviews page; raw saved to `data/raw/appstore_reviews.json` |

Collection script: `scripts/collect_appstore.py` (public endpoint only; no UC scraping). This is a **single-source, complaint-heavy** corpus; the bias report and deck state that limitation explicitly. Other source classes below remain available to add via the Discovery Engine paste/upload, but are not yet collected.

## Not accessed
- Urban Company logged-in app/web account surfaces.
- Private customer data, booking history exports, internal UC analytics.
- Screenshots, invoices, addresses, phone numbers, personal documents from respondents.
- Any paywalled/private sources requiring credentials.
