# Urban Company — Home Care Companion (NextLeap Graduation Project)

Public, customer-side prototype for the NextLeap PM Fellowship Graduation Project (Nov 2026, PMF Cohort 52).  
**Constraint:** No bookings, no account access, no discounts/coupons/pricing/professional-pay changes. Public information only.

## What this repo contains
- **Home Care Companion MVP** (Streamlit): 4-step wizard — profile, 90-day calendar, Need Decider, post-service reflection.
- **AI Discovery Engine**: ingests public feedback, codes into fixed T1–T11 taxonomy, aggregates, bias report, golden-set evaluation.
- **Evidence Log**: sources/volume, agreement, per-theme precision/recall, confusion matrix, corrections, bias/limitations.
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
        ├── src/eval.py  ── golden set, agreement, evidence log
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

## Run locally

```powershell
cd C:\Users\Daman-Simran\Desktop\NextLeap-PMF-Projects-2026\NextLeap-A1-UC-GP-23-November-2026
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env  # optional: add GEMINI_API_KEY
streamlit run app.py
```

## Run the pipeline

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

## Re-collect data (public only)
1. Collect **public** feedback only (app store reviews, public forums, public social posts, public transcripts). Do **not** scrape logged-in Urban Company surfaces or use private data.
2. Put rows in `data/public_corpus.csv` with columns: `source,text,date,url,source_class,rating,geography,category,language,is_illustrative,notes`.
3. Run `python -m src.ingest` or use Discovery Engine upload.
4. Manually label 20 rows in `data/golden_set.csv` (`human_theme_code`, `human_return_signal`). **Do not fabricate labels.**
5. Add 5–6 anonymized interviews in `data/interviews.csv` (R01–R06; no PII).

## Deployed URLs (placeholders)
- Streamlit app: `<ADD_STREAMLIT_CLOUD_URL>`
- Evidence log: `<ADD_PUBLIC_EVIDENCE_LOG_URL>`
- Deck PDF: `<ADD_PUBLIC_DECK_PDF_URL>`

## Submission checklist
- [ ] `docs/constraints.md` respected; no C1/C2/C3 violations.
- [ ] Public corpus collected (real public data, not only illustrative sample).
- [ ] `data/golden_set.csv` has 20 manually labelled rows.
- [ ] `data/interviews.csv` has 5–6 anonymized interviews (R01–R06), both returner values, >=2 categories.
- [ ] >=3 MVP user tests completed; `views/7_MVP_Testing.py` updated.
- [ ] `outputs/evidence_log.md` and `outputs/evidence_log.pdf` generated.
- [ ] `outputs/NL_UrbanCompany.pdf` built (10 slides max, no fellow name).
- [ ] `python -m scripts.qa_check` passes.
- [ ] App deployed on Streamlit Cloud; public links added above.
- [ ] `config.FELLOW_NAME_TO_EXCLUDE` set locally before final deck QA (do not commit personal name).
