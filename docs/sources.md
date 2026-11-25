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
| Public stock imagery | Free-license home-interior photography for UI background only | https://www.pexels.com/photo/1080721/ (Pexels License) | Public CDN image, no login | Logged-in pages, images requiring attribution fees or private licences |

## Actually collected (real, not illustrative)

| Date | Source | Method | Volume | Provenance |
|---|---|---|---|---|
| 2026-11-23 | App Store (India) — Urban Company app id `1032480595` | Apple public customer-reviews RSS/JSON (`itunes.apple.com/in/rss/customerreviews/...`), pages 1–10, no login | 500 fetched → 465 kept after ingest (PII redaction, <20-char drop, dedupe) | `source_url` = public App Store reviews page; raw saved to `data/raw/appstore_reviews.json` |
| 2026-11-25 | Google Play (India) — `com.urbanclap.urbanclap` | Public Play Store review endpoint via `google-play-scraper`, English/India, newest first, no login | 250 fetched → 163 added after dedupe; merged corpus 663 rows | `source_url` = public Play Store listing; raw saved to `data/raw/playstore_reviews.json` |
| 2026-11-25 | Pexels free photo `1080721` — bright, people-free living room | Public CDN `images.pexels.com/photos/1080721/pexels-photo-1080721.jpeg`, Pexels License, no login | 1 image saved as `assets/about_background.jpg` | Used only as About-card visual in the MVP; no UC account/app content |

Collection scripts: `scripts/collect_appstore.py` and `scripts/collect_playstore.py` (public endpoints only; no UC account/app scraping). The active corpus is `data/public_corpus_merged.csv`; `data/public_corpus.csv` is retained as the App Store-only snapshot. `scripts/probe_public_sources.py` records public-source availability in `outputs/source_availability.json`: Trustpilot and Reddit search returned HTTP 403 from this environment and contributed **no** data. The corpus is now **two-source but still app-store/complaint-heavy**; the bias report, deck, and evidence log state that limitation explicitly. Remaining source classes can be added via the Discovery Engine paste/upload path or new collectors.

## Not accessed
- Urban Company logged-in app/web account surfaces.
- Private customer data, booking history exports, internal UC analytics.
- Screenshots, invoices, addresses, phone numbers, personal documents from respondents.
- Any paywalled/private sources requiring credentials.
