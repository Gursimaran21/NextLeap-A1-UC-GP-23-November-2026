# Cursor + Gemini Prompt Pack — UC Graduation Project

Use these prompts in order. Prepend every prompt with: **“Respect docs/constraints.md.”**  
Do not fabricate golden labels, interviews, user-test observations, or private data.

## P0 — Brief + constraints
> Respect docs/constraints.md. Read the project brief and create `docs/brief.md` and `docs/constraints.md` with C1–C10 guardrails, QA assertions (BLOCKER/WARN), forbidden patterns, and canonical 90-day metric definition.

## P1 — Scaffold
> Respect docs/constraints.md. Scaffold the Streamlit project in the target folder without overwriting existing brief/constraints. Create app/views/src/data/docs/prompts/scripts/.streamlit/requirements/env/gitignore placeholders. Use Python 3.11, streamlit, pandas, scikit-learn, reportlab, pypdf, python-dotenv, altair; optional google-genai.

## P2 — Config
> Respect docs/constraints.md. Implement `src/config.py` with paths, C4/C5 metric constants, T1–T11 themes, bias flags, return signals, source classes, segment, D1–D6 decomposition, palette, limits, forbidden patterns, `FELLOW_NAME_TO_EXCLUDE`, and `DECK_PDF_NAME`.

## P3 — PII + ingest
> Respect docs/constraints.md. Implement `src/pii.py` and `src/ingest.py`. Redact PII, enforce C3 (no logged-in UC scraping), validate corpus schema, dedupe, and build illustrative sample corpus. Verify: `python -m src.pii` and sample corpus build.

## P4 — Taxonomy + engine + LLM
> Respect docs/constraints.md. Implement `src/taxonomy.py`, `src/llm.py`, `src/engine.py`. LLM must have strict JSON, fence stripping, retry, and offline deterministic fallback. Engine must always return fully populated schema; deterministic fallback never returns None.

## P5 — Eval + export
> Respect docs/constraints.md. Implement `src/eval.py` and `src/export.py`. Generate 20-row golden template with TODO labels; never fabricate labels. Compute agreement, per-theme precision/recall, confusion matrix, disagreements. Export evidence_log.md/pdf.

## P6 — Opportunity scoring
> Respect docs/constraints.md. Implement `src/opportunity.py`. Map themes to D1–D6, score opportunities, exclude T9/C1-forbidden solution directions.

## P7 — MVP logic
> Respect docs/constraints.md. Implement `src/mvp.py`. Deterministic-first router: URGENT/DIY/LOCAL/UC_CATEGORY/WAIT_AND_WATCH/SEEK_IMMEDIATE_HELP. No booking/account actions. Log tool traces to `outputs/tool_trace.jsonl`. Use public reference only.

## P8 — App shell
> Respect docs/constraints.md. Create `app.py` with `st.set_page_config`, secret mirroring for GEMINI keys, shared CSS, `st.navigation`/`st.Page`, MVP default, and sidebar footer “Public prototype · No bookings · No account access · Public information only”.

## P9 — Discovery + Evidence pages
> Respect docs/constraints.md. Build `views/2_Discovery_Engine.py` and `views/3_Evidence_Log.py`. Discovery: ingest/code/aggregate/bias, charts, quotes, how-it-works block, JSON download. Evidence: sources, golden agreement, confusion matrix, corrections, bias, limitations, MD/PDF downloads. Generate downloads on demand (ephemeral-disk friendly).

## P10 — MVP UI
> Respect docs/constraints.md. Build `views/1_MVP.py` 4-step wizard: profile (no PII), 90-day calendar (public basis/source/confidence), Need Decider (route + reason + why-not + clarifying + tool chip), post-service reflection (private checklist download, feedback). No booking/account actions.

## P11 — Research/problem/testing/metrics/risks
> Respect docs/constraints.md. Create `src/research.py` and views 4–9. Validate anonymized interviews (R01–R06, no PII columns). Include metric decomposition, research protocol/synthesis placeholders, problem statement with “not bad experience, not offer” callout, MVP testing plan, success/guardrail metrics, 10 tool-choice golden tasks, 6 risks.

## P12 — Deck
> Respect docs/constraints.md. Create `src/deck.py` and `views/10_Deck.py`. 10 message-first slides, A4 landscape PDF, 14pt min body/22pt title, palette, footer page numbers, no fellow name, filename `NL_UrbanCompany.pdf`. QA: pages <=10, size <40MB, fellow name absent.

## P13 — QA/docs/deploy
> Respect docs/constraints.md. Create `scripts/qa_check.py`, `docs/qa_report.md`, `README.md`, `docs/deploy_streamlit_cloud.md`, `docs/sources.md`, `docs/methodology.md`, `docs/demo_script.md`. Run `python -m scripts.qa_check`. Do not fabricate missing golden/interview data; report blockers.

## Verification loop
```powershell
pip install -r requirements.txt
python -m src.pii
python -c "import src.ingest as i; print(i.build_sample_corpus().shape)"
python -m src.engine
python -m src.eval
python -m src.deck
python -m scripts.qa_check
streamlit run app.py
```

## Deploy
```powershell
git init
git add .
git commit -m "UC graduation project"
git remote add origin <REPO_URL>
git branch -M main
git push -u origin main
```
Deploy on Streamlit Cloud: main file `app.py`, secrets `GEMINI_API_KEY` (optional), use download buttons for deliverables (ephemeral disk).
