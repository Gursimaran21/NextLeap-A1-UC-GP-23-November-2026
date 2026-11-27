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
| Public company website | About Us framing, business units, city-page service groups | https://www.urbancompany.com/* | Public pages, no login | Logged-in account/app surfaces; prices, offers and booking CTAs are not reused |
| Primary interviews | Anonymized notes/quotes (R01–R06) | N/A (offline collection) | Consent-based, anonymized | Names, phone, address, screenshots, invoices, personal docs |
| User-provided / public website imagery | Home-care service photography for UI background only | Local `assets/about_background_1.jpg`; earlier public URL `https://juccleaningservices.com/assets/img/banda/kitchen-deep-cleaning.webp` | Supplied by user / public static asset, no login | Logged-in pages, private/paywalled image libraries |

## Actually collected (real, not illustrative)

| Date | Source | Method | Volume | Provenance |
|---|---|---|---|---|
| 2026-11-23 | App Store (India) — Urban Company app id `1032480595` | Apple public customer-reviews RSS/JSON (`itunes.apple.com/in/rss/customerreviews/...`), pages 1–10, no login | 500 fetched → 465 kept after ingest (PII redaction, <20-char drop, dedupe) | `source_url` = public App Store reviews page; raw saved to `data/raw/appstore_reviews.json` |
| 2026-11-25 | Google Play (India) — `com.urbanclap.urbanclap` | Public Play Store review endpoint via `google-play-scraper`, English/India, newest first, no login | 250 fetched → 163 added after dedupe; merged corpus 663 rows | `source_url` = public Play Store listing; raw saved to `data/raw/playstore_reviews.json` |
| 2026-11-27 | Public reference freshness check | Public HEAD/GET checks and public web search index, no login | 15 rows in `data/public_reference.csv` | `freshness` and `match_strength` now recorded; CDC cleaning row updated to `https://www.cdc.gov/hygiene/about/when-and-how-to-clean-and-disinfect-your-home.html` (page dated 2025-01-31); direct-fetch-blocked pages are labelled `blocked_2026-11` and are not treated as verified |
| 2026-11-25 | User-provided About-card image | User added `assets/about_background_1.jpg` locally; earlier JUC Cleaning Services image was fetched from a public URL without login | 1 active image (`assets/about_background_1.jpg`); previous image retained as `assets/about_background.jpg` | Used only as About-card visual in the MVP; no UC account/app content |
| 2026-11-26 | Urban Company public About Us page | Direct public read of `https://www.urbancompany.com/about`, no login | High-level company and business-unit framing; footer figures as on 31 Dec 2024 | Leadership names, private data and account surfaces not reused |
| 2026-11-26 | Urban Company public Chennai city page | Direct public read of `https://www.urbancompany.com/chennai`, no login | Service-category structure and public trust figures | No prices, offers, bookings, payments or account actions used in the app |
| 2026-11-26 | Reuters — Snabbit funding and scale | Public article excerpt via web search, no login: https://www.reuters.com/world/india/indian-instant-home-services-platform-snabbit-raises-56-million-fresh-funding-2026-04-28 | Funding, scale, monthly jobs and market context for `views/11_Competitors.py` | Private dashboards, audited financials, account data |
| 2026-11-26 | TechCrunch — Snabbit 2025 operating model | Public article excerpt via web search, no login: https://techcrunch.com/2025/10/29/indias-snabbit-valuation-doubled-to-180m-in-5-months-on-its-quick-house-help-bet | Fleet, micromarkets, retention and category context | Private contracts, worker-level data, logged-in app surfaces |
| 2026-11-26 | TechCrunch — Snabbit Series D 2026 | Public article excerpt via web search, no login: https://techcrunch.com/2026/04/27/indias-snabbit-closes-56m-round-as-investor-interest-heats-up-in-on-demand-home-services | Worker count, daily jobs and valuation context | Private financial statements, investor-only material |
| 2026-11-26 | YourStory — Snabbit salon-at-home pilot | Public article excerpt via web search, no login: https://yourstory.com/2026/05/snabbit-instant-salon-at-home-services-challenge-urban-company | Category expansion into instant salon-at-home | Private pilot data, customer lists, account data |
| 2026-11-26 | Reuters — Pronto funding and scale | Public article excerpt via web search, no login: https://www.reuters.com/world/india/indian-instant-home-services-startup-pronto-raises-20-million-valuation-doubles-2026-05-07 | Funding, valuation, daily bookings and expansion | Private dashboards, audited financials, account data |
| 2026-11-26 | TechCrunch — Pronto 2026 company profile | Public article excerpt via web search, no login: https://techcrunch.com/2026/03/02/indias-pronto-formalizes-house-help-as-its-valuation-jumps-8x-in-under-a-year | Operating model, funding, daily active users and market context | Private worker data, logged-in app surfaces |
| 2026-11-26 | TechCrunch — Pronto additional Series B capital | Public article excerpt via web search, no login: https://techcrunch.com/2026/05/06/a-20-minute-pitch-wins-indian-startup-pronto-backing-from-lachy-groom | Additional funding and category-sizing context | Private term sheets, investor-only material |
| 2026-11-26 | Reuters — Urban Company instant-services focus | Public article excerpt via web search, no login: https://www.reuters.com/world/india/indias-urban-company-plans-big-bet-instant-home-services-ceo-says-2025-09-19 | Public context for Urban Company's instant-services strategy | Internal plans, private metrics, account data |

Collection scripts: `scripts/collect_appstore.py` and `scripts/collect_playstore.py` (public endpoints only; no UC account/app scraping). The active corpus is `data/public_corpus_merged.csv`; `data/public_corpus.csv` is retained as the App Store-only snapshot. `scripts/probe_public_sources.py` records public-source availability in `outputs/source_availability.json`: Trustpilot and Reddit search returned HTTP 403 from this environment and contributed **no** data. The corpus is now **two-source but still app-store/complaint-heavy**; the bias report, deck, and evidence log state that limitation explicitly. Remaining source classes can be added via the Discovery Engine paste/upload path or new collectors.

## Not accessed
- Urban Company logged-in app/web account surfaces.
- Private customer data, booking history exports, internal UC analytics.
- Screenshots, invoices, addresses, phone numbers, personal documents from respondents.
- Any paywalled/private sources requiring credentials.
