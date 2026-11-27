# Constraints — Urban Company Graduation Project (Nov 2026, PMF Cohort 52)

> **Rule:** EVERY later prompt, code change, and deliverable review must begin with: **"Respect docs/constraints.md"**.  
> If a proposed feature conflicts with these constraints, the constraint wins.

## 1. Constraint Table (C1–C10)

| ID | Constraint | How it will be enforced in code / process |
|---|---|---|
| **C1** | **No discounts, coupons, memberships, pricing changes, or changes to professional pay/management.** Solution must work from the customer's side. | `scripts/qa_check.py` scans all MVP/UI/deck/output text for forbidden patterns (discount, coupon, promo, cashback, membership, free trial, price change, professional pay/earnings/commission, incentive). `src/mvp.py` route responses are template-guarded; any LLM response passes a post-filter before display. Deck/problem pages include an explicit "out of scope" callout. |
| **C2** | **MVP must not book services, message Urban Company or service professionals, or take any action on a customer's account on their behalf.** | MVP has no booking/messaging/account APIs, no UC auth, no write endpoints. `scripts/qa_check.py` asserts no `requests`/`httpx`/`urllib`/`selenium` calls to Urban Company domains in MVP code, and no CTA strings like "book now", "schedule", "pay", "checkout", "message professional". UI footer states: "Public prototype · No bookings · No account access · Public information only". |
| **C3** | **Use only sources you are permitted to access. Do not scrape logged-in Urban Company pages or the app.** | `data/public_corpus.csv` requires `source_url`, `source_class`, `access_date`, and `access_type=public`. `src/ingest.py` rejects rows whose URL/path suggests logged-in/app/account content. `docs/sources.md` logs every source class and what was not accessed. No scraping scripts for UC app/logged-in pages in repo. |
| **C4** | **Exact anchor definition.** Pick a month. Every customer whose first completed booking in that month was in a core category is counted once; that booking is their anchor booking. Quick-service housekeeping (InstaHelp) excluded. | `src/config.py` defines `ANCHOR_MONTH`, `CORE_CATEGORIES`, `EXCLUDED_CATEGORIES=["InstaHelp"]`. Metric/decomposition pages render the exact definition from config. Any analysis code filters anchor candidates by first-completed-in-month + core category + not InstaHelp. |
| **C5** | **Exact 90-day return definition.** A customer "books another service" if they complete any later booking, in any category, within 90 days of the anchor booking. Redos, warranty claims, and bookings that end in a refund do not count. | `src/config.py` defines `WINDOW_DAYS=90`, `RETURN_COUNTS_ANY_CATEGORY=True`, `EXCLUDED_OUTCOMES=["redo","warranty","refund","refunded"]`. Metric page and deck include this definition verbatim/clearly. Any simulated/calculation logic excludes redos/warranty/refunds. |
| **C6** | **5–6 user interviews; respondents completed a UC booking in last 6 months; include both returners and non-returners within 90 days; cover more than one service category; record total bookings each.** | `src/research.py` validates `data/interviews.csv`: 5–6 rows, `returner_90d` contains both yes/no, >=2 `category` values, `total_bookings` present as int. `scripts/qa_check.py` reports BLOCKER if missing before final submission; WARN during drafting. Research page displays anonymized table. |
| **C7** | **Do not collect booking screenshots, invoices, addresses, phone numbers or other personal documents from respondents.** | Interview intake template excludes those fields. `src/pii.py` redacts emails/phones/UPI/long IDs/URLs/handles; `src/research.py` rejects PII-like columns (`name`, `phone`, `address`, `email`, `invoice`, `screenshot`, `document`). QA scan checks interview/corpus/output files for PII patterns. Research page shows anonymity notice. |
| **C8** | **Deck: 10 slides max (title counts), no fellow name anywhere, message-first slide titles, readable background, colour-blind-safe colours, hyperlinked artefacts with access, <40 MB, correct naming, minimum font size rules.** | `src/deck.py` enforces slide count <=10, uses message-first titles, defined styles with min font >=14pt for PPT-equivalent reportlab styles, and exports `NL_UrbanCompany.pdf`. `scripts/qa_check.py` checks page count, file size <40MB, absence of `FELLOW_NAME_TO_EXCLUDE`, and presence of hyperlinks/artefact refs. Visual colour/contrast reviewed manually (QA checklist). |
| **C9** | **All four deliverables accessible through Streamlit/public links.** MVP is the root Streamlit page; Discovery Engine, Evidence Log, and Deck are Streamlit pages with stable URLs; PDF/MD downloads provided where required. | `app.py` uses `st.navigation`/`st.Page` with explicit routes. `docs/deploy_streamlit_cloud.md` documents deployment. README lists all four deliverable URLs. QA checklist verifies each link opens in incognito/public context. |
| **C10** | **AI Evidence Log is one document with view access for anyone with the link.** Must include sources & volume, ~20-item golden set hand-labelled, engine agreement/failures, and 2–3 rejected/corrected AI outputs with why. | Evidence Log page renders all required sections and offers MD/PDF download. `src/eval.py` computes agreement only from hand-labelled golden rows (no fabricated labels). QA checks: golden set has 20 labelled rows, corrections >=2, sources table present, doc downloadable/public-page accessible. |

## 2. Forbidden Phrases / Patterns

These must **not** appear in MVP copy, deck problem framing, generated recommendations, or solution rationale (except inside this constraints doc or QA test definitions).

| Category | Forbidden examples / patterns |
|---|---|
| **Discounts/incentives** | discount, coupon, promo code, cashback, offer, deal, free trial, membership, loyalty points, voucher, referral bonus, "come back and save" |
| **Pricing changes** | price change, lower price, cheaper, surge pricing change, fee waiver, reduce charges |
| **Professional-side changes** | professional pay, partner earnings, commission change, incentive for professionals, penalize professionals, change partner management, rating penalty |
| **Bad framing (prohibited root-cause shortcuts)** | "Customers had a bad experience." / "bad experience" as the sole root cause; "Customers need an offer to come back." |
| **Account/action CTAs** | book now, book again, schedule now, pay now, checkout, message professional, contact pro, cancel booking, modify booking |

**Allowed framing:** identify why customers did or did not return even when nothing went wrong; focus on customer-side planning, awareness, decision confidence, timing, and continuity.

## 3. Metric Definition (Canonical)

Use this exact meaning everywhere (config, UI, deck, evidence):

- **Business metric:** Share of customers who complete another booking within 90 days of a completed booking.
- **Anchor booking:** Pick a month. Every customer whose **first completed booking in that month** was in a **core category** is counted once. That booking is their anchor booking. **Quick-service housekeeping (InstaHelp) is excluded**.
- **Return / "books another service":** Customer completes **any later booking, in any category, within 90 days** of the anchor booking.
- **Do not count:** Redos, warranty claims, and bookings that end in a refund.
- **Business context:** About **84% of Urban Company's net transaction value** comes from repeat customers.

## 4. QA Assertions (Automated / Checklist)

The final app must pass these before submission. `scripts/qa_check.py` should report **BLOCKER** or **WARN**.

| ID | Assertion | Type |
|---|---|---|
| QA-01 | No forbidden phrases/patterns (C1, forbidden framing, booking CTAs) in `src/mvp.py`, MVP views, deck text, generated outputs. | BLOCKER |
| QA-02 | No booking/messaging/account-action code paths; no UC-domain network calls in MVP. | BLOCKER |
| QA-03 | Corpus rows have public source URL/class/date; no logged-in UC/app scraping code or URLs flagged as private. | BLOCKER |
| QA-04 | Metric definition in config/UI matches C4/C5 exactly (anchor month rule, core category, InstaHelp excluded, 90 days, any category, redo/warranty/refund excluded). | BLOCKER |
| QA-05 | Golden set has ~20 hand-labelled rows; agreement computed only on labelled rows; no fabricated labels. | BLOCKER before submit / WARN during draft |
| QA-06 | Evidence log contains sources & volume, golden-set agreement, failures, and >=2 corrected/rejected AI outputs with reasons. | BLOCKER |
| QA-07 | Interviews dataset has 5–6 rows, both returner/non-returner present, >1 category, `total_bookings` recorded, no PII columns/values. | BLOCKER before submit / WARN during draft |
| QA-08 | MVP user test has >=3 return users from target segment with real task, observations, and next-iteration changes. | BLOCKER before submit / WARN during draft |
| QA-09 | Deck is <=10 slides, <40 MB, named `NL_UrbanCompany.pdf` (or chosen final name following NL_ pattern), no fellow name, message-first titles, min font rules satisfied by style config. | BLOCKER |
| QA-10 | All four deliverables reachable: Discovery Engine link, MVP link, Evidence Log link/doc, Deck PDF. Links work in public/incognito context. | BLOCKER |
| QA-11 | App runs with no API key (deterministic fallback) and does not crash on missing optional secrets. | BLOCKER |
| QA-12 | PII scan passes on corpus, interviews, outputs, and logs; no screenshots/invoices/addresses/phones/docs collected. | BLOCKER |

## 5. Working Rules

- **Public evidence only:** Store source URL, access date, and source class for every external item.
- **No fabricated evidence:** Do not invent interview quotes, labels, agreement scores, or user feedback. Use `TODO`/`TO_FILL` placeholders until real data exists.
- **Honest AI:** Discovery/eval pages must show where AI was wrong, uncertain, or biased.
- **Customer-side only:** Solutions may change customer information, planning, reflection, or decision support — not pricing, incentives, pro management, or UC account actions.
- **Accessibility/readability:** Colour is never the only encoding; maintain readable contrast; minimum font sizes per deck guideline.