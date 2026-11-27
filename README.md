# Urban Company — Home Care Companion

Public, customer-side prototype for the **NextLeap PM Fellowship Graduation Project** (Nov 2026, PMF Cohort 52).  
**Constraint:** No bookings, no account access, no discounts/coupons/pricing/professional-pay changes. Public information only.  
All work must respect [`docs/constraints.md`](docs/constraints.md).

## Key Docs

| Doc | Purpose |
|---|---|
| [`PRD.md`](PRD.md) | Product requirements, scope, acceptance criteria, milestones |
| [`docs/brief.md`](docs/brief.md) | Original graduation project brief |
| [`docs/constraints.md`](docs/constraints.md) | Canonical C1–C10 constraints and QA assertions |
| [`docs/methodology.md`](docs/methodology.md) | Discovery/evaluation methodology |
| [`docs/sources.md`](docs/sources.md) | Public source log and access notes |
| [`docs/deploy_streamlit_cloud.md`](docs/deploy_streamlit_cloud.md) | Streamlit Cloud deployment guide |
| [`docs/interview_guide.md`](docs/interview_guide.md) | Ready-to-run kit for the 5–6 anonymized interviews (C6/C7) |
| [`docs/mvp_test_script.md`](docs/mvp_test_script.md) | Moderator script + tasks for the 3 real MVP user tests |
| [`docs/qa_report.md`](docs/qa_report.md) | QA report snapshot |
| [`prompts/cursor-gemini-prompts.md`](prompts/cursor-gemini-prompts.md) | Cursor/Gemini prompt pack (P0–P13) |

## Current Status

- **Build:** MVP, Discovery Engine, Evidence Log, Research/Strategy pages, and 10-slide deck are implemented.
- **Real data:** `data/public_corpus.csv` now holds **500 real public App Store (India) reviews** (465 kept after cleaning), collected 2026-11-23 via `scripts/collect_appstore.py`. Discovery results, evidence log, and deck regenerated from real data. Golden template regenerated from real reviews (20 rows, unlabelled).
- **QA:** `python -m scripts.qa_check` currently reports **11/12 PASS**.
  - Failing: golden set has 0/20 manually labelled rows (do not fabricate).
- **Pending before submission:** 20 manual golden labels (`python -m scripts.label_golden`), 5–6 real anonymized interviews, >=3 MVP user tests, fellow-name exclusion set locally, final QA pass, Streamlit deployment/public links.

## What This Repo Contains

- **Home Care Companion MVP** (Streamlit): 4-step wizard — anonymous household profile + optional service history, private 90-day plan with grounded summary and Markdown/.ics/JSON export, Need Decider with explicit no-action route, and post-service reflection checklist.
- **AI Discovery Engine**: ingests public feedback, codes into fixed T1–T11 taxonomy, aggregates, bias report, golden-set evaluation.
- **Evidence Log**: sources/volume, agreement, per-theme precision/recall, confusion matrix, corrections, bias/limitations; MD/PDF downloads.
- **Deck**: 10-slide message-first PDF (`outputs/NL_UrbanCompany.pdf`).
- **QA**: `python -m scripts.qa_check`.

## Architecture

```text
Public sources (CSV/paste/public URLs metadata)
        │
        ▼
src/ingest.py  ── PII redaction, C3 guard, dedupe
        │
        ▼
src/engine.py  ── T1–T11 coding (LLM or deterministic fallback)
        │
        ├── src/eval.py        ── golden set, agreement, evidence log
        ├── src/opportunity.py ── D1–D6 opportunity ranking (T9 excluded)
        ▼
outputs/discovery_results.json, evidence_log.md/pdf
        │
        ▼
Streamlit app (app.py + views/*)
  - MVP (src/mvp.py): build_calendar, route_need, reflect
  - Discovery/Evidence/Research/Problem/Testing/Metrics/Risks/Deck
        │
        ▼
outputs/NL_UrbanCompany.pdf, tool_trace.jsonl, mvp_feedback.jsonl
```

## Run Locally

```powershell
cd C:\Users\Daman-Simran\Desktop\NextLeap-PMF-Projects-2026\NextLeap-A1-UC-GP-23-November-2026
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env  # optional: add GEMINI_API_KEY
streamlit run app.py
```

Optional LLM: set `GEMINI_API_KEY` in `.env` or Streamlit secrets. The app should run without it using deterministic fallback.

## Run the Pipeline

```powershell
# Build/load sample corpus and run discovery
python -m src.ingest
python -m src.engine

# Generate golden template / evaluate (after manual labeling)
python -m src.eval

# Build deck PDF
python -m src.deck

# Run QA
python -m scripts.qa_check
```

## Data Files (Public / Anonymized Only)

| File | Expected columns | Notes |
|---|---|---|
| `data/public_corpus.csv` | `item_id,source,source_class,source_url,access_date,text,rating,city,category,return_signal_hint,is_illustrative` | Public sources only (C3). No logged-in UC/app scraping. |
| `data/golden_set.csv` | `item_id,text,human_primary_theme,human_return_signal,human_note` | 20 rows manually labelled; **do not fabricate labels**. |
| `data/interviews.csv` | `respondent_id,interview_date,consent,city_tier,household_type,decision_maker,last_booking_date,category,total_bookings,anchor_booking_date,return_90d,subsequent_need,Q4_discovery,Q5_booking_reason,Q6_provider_choice,Q7_post_service,Q8_expectations,Q9_next_need,Q10_arrangement,Q11_considered_UC,Q12_alternative,Q13_return_motivation,Q14_barriers,Q15_planning,Q16_tracking_value,Q17_decision_information,Q18_usefulness,main_barrier,researcher_notes,quote,theme_code` | 5–6 anonymized interviews (R01–R06), both `return_90d` yes/no, >=2 `category` values, no PII (C6/C7). |
| `data/public_reference.csv` | `need,trigger,typical_timing_days,public_basis,source_url,source_class` | Public, non-UC-specific reference facts with sources. |

## Re-collect / Replace Data

1. Collect **public** feedback only (app stores, public forums, public social posts, public transcripts). Do **not** scrape logged-in Urban Company surfaces or use private data.
   - App Store (India) reviews can be refreshed with `python -m scripts.collect_appstore` (public Apple RSS endpoint).
2. Replace or append rows in `data/public_corpus.csv` with the schema above; keep provenance (`source_url`, `access_date`, `source_class`).
3. Run discovery via `python -m src.engine` or the Discovery Engine page.
4. Manually label 20 rows in `data/golden_set.csv`. Do not fabricate labels.
5. Replace `data/interviews.csv` placeholders with 5–6 real anonymized interviews.
6. Run >=3 MVP user tests and update `views/7_MVP_Testing.py`.

## Deliverables

| Deliverable | App / Artifact | Status |
|---|---|---|
| AI Discovery Engine | `views/2_Discovery_Engine.py` | Implemented |
| 10-slide deck | `outputs/NL_UrbanCompany.pdf`, `views/10_Deck.py` | Draft generated |
| Deployed AI-native MVP | `app.py`, `views/1_MVP.py` | Implemented locally with history input, plan export, reminders, and explicit no-action; deploy pending |
| AI Evidence Log | `views/3_Evidence_Log.py`, `outputs/evidence_log.md`, `outputs/evidence_log.pdf` | Draft generated |

## Deployed URLs

- Streamlit app: `<ADD_STREAMLIT_CLOUD_URL>`
- Evidence log: `<ADD_PUBLIC_EVIDENCE_LOG_URL>`
- Deck PDF: `<ADD_PUBLIC_DECK_PDF_URL>`

## Submission Checklist

- [ ] `docs/constraints.md` respected; no C1/C2/C3 violations.
- [x] Public corpus collected (real public data, not only illustrative sample) — 500 App Store (India) reviews, 2026-11-23.
- [ ] `data/golden_set.csv` has 20 manually labelled rows.
- [ ] `data/interviews.csv` has 5–6 real anonymized interviews (R01–R06), both `return_90d` values, >=2 `category` values.
- [ ] >=3 MVP user tests completed; `views/7_MVP_Testing.py` updated.
- [ ] `outputs/evidence_log.md` and `outputs/evidence_log.pdf` regenerated after real data updates.
- [ ] `outputs/NL_UrbanCompany.pdf` rebuilt (10 slides max, no fellow name).
- [ ] `python -m scripts.qa_check` passes (target 12/12).
- [ ] App deployed on Streamlit Cloud; public links added above.
- [ ] `config.FELLOW_NAME_TO_EXCLUDE` set locally before final deck QA (do not commit personal name).
