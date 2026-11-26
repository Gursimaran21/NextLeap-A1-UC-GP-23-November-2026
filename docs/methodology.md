# Methodology

## 1) Scope and constraints
- Problem: increase 90-day repeat completion among eligible customers, customer-side only.
- Constraints: no discounts/coupons/membership/pricing/professional-pay changes (C1); no booking/messaging/account actions in MVP (C2); public sources only (C3); exact metric definition (C4/C5); anonymized interviews (C6/C7); 10-slide deck rules (C8); Streamlit/public deliverables (C9/C10).

## 2) Metric and decomposition
- Anchor: first completed core-category booking in anchor month; customer counted once.
- Return: any completed booking in any category within 90 days.
- Exclude: InstaHelp, redos, warranty, refunds.
- Decompose D1–D6: need incidence, recognition, mental availability, category consideration, choice vs alternatives, frictionless completion. Focus on influencable customer-side stages D2–D5.

## 3) AI discovery engine
- **Ingest:** public CSV/paste with source, date, URL, source_class. Block logged-in UC/app paths. Redact PII. Dedupe.
- **Code:** fixed T1–T11 taxonomy. LLM assigns theme when available; deterministic keyword/rule fallback otherwise. Output includes theme, return signal, bias flag, confidence, evidence.
- **Aggregate:** theme distribution, continuity vs experience split, source mix, top quotes.
- **Validate:** 20-row human-labelled golden set. Report agreement, per-theme precision/recall, confusion matrix. No fabricated labels.
- **Bias handling:** vocal-negative overrepresentation, silent-nonreturner proxy, public-source skew. Evidence log records limitations and corrections.

## 4) Primary research
- 5–6 anonymized interviews, R01–R06. No PII/screenshots/invoices/docs.
- Coverage: at least 1 returner, 1 non-returner, 2 categories, 1 low-frequency user (2+ bookings).
- Synthesis compares AI findings vs interview validation/challenges.

## 5) MVP
- 4-step Home Care Companion: anonymous profile + optional service history, private plan, Need Decider, reflection.
- Plan cues combine customer-provided timing/issue/upcoming notes with public-reference cadence; every cue shows basis, source, evidence type and confidence.
- Explicit no-need path: multiselect for categories not needed, plus a Need Decider `NO_ACTION` route.
- Exports: private Markdown plan, JSON plan data, and `.ics` calendar with one-day-before reminders.
- Deterministic-first Need Decider with optional LLM enhancement; grounded plan summary with deterministic fallback.
- Routes: DIY, LOCAL_OR_NEIGHBOUR, UC_CATEGORY, WAIT_AND_WATCH, SEEK_IMMEDIATE_HELP, NO_ACTION.
- Tool traces logged to `outputs/tool_trace.jsonl` for audit.
- No transactions, no account access, no PII collection, no external scraping.

## 6) Evaluation
- Golden-task routing audit (10 tasks) for tool-choice precision/recall.
- 3 return-user concept tests; capture observed behavior and iteration changes.
- Guardrails: non-UC route rate, no-need rate, 2-week “did I actually need it?” follow-up.

## 7) QA
- `python -m scripts.qa_check` checks C1/C2/C3 patterns, golden/interview coverage, deck rules, evidence artefacts.
- Manual pre-submit: set `FELLOW_NAME_TO_EXCLUDE` locally, verify public links, verify no PII/secrets.
