# PRD — Urban Company Home Care Companion

> **Respect `docs/constraints.md`.** This PRD defines the product, scope, and acceptance criteria for the NextLeap Urban Company Graduation Project (Nov 2026, PMF Cohort 52). If any requirement conflicts with `docs/constraints.md`, the constraint wins.

## 1. Document Control

| Field | Value |
|---|---|
| **Product** | Urban Company — Home Care Companion (customer-side prototype) |
| **Project** | NextLeap PM Fellowship Graduation Project, Nov 2026, PMF Cohort 52 |
| **Owner** | Fellow (name excluded from deck per C8) |
| **Status** | Draft / in build |
| **Primary docs** | `docs/brief.md`, `docs/constraints.md`, `README.md` |
| **Submission deadline** | Dec 13, 2026, 3:59:00 PM IST |

## 2. Problem Statement

Urban Company customers complete a home service, but many do not complete another booking within 90 days. The team does not know what separates customers who return from those who do not. Public feedback over-represents bad experiences, and silent non-returners leave little trace.

The product opportunity is to **discover the customer-side reason for non-return** and build a customer-side MVP that helps customers recognize, plan, and decide on legitimate home-care needs — without incentives, pricing changes, professional-side changes, or account actions.

## 3. Goals

| Goal | Description | Success signal |
|---|---|---|
| **G1. Discover** | Build an AI-powered discovery engine that codes public feedback into opportunity themes and surfaces evidence quality/bias. | Engine runs on public corpus; outputs T1–T11 themes, bias report, golden-set evaluation, evidence log. |
| **G2. Define** | Decompose the business metric, validate with primary research, and define a clear customer-side problem. | D1–D6 decomposition, 5–6 anonymized interviews, problem definition grounded in evidence. |
| **G3. Build** | Ship a functional, publicly testable MVP that works from customer input and public information only. | Streamlit MVP deployed; 4-step flow usable without API key; no booking/account actions. |
| **G4. Validate** | Test the MVP with target users and define success/guardrails. | >=3 user tests with observations and iteration changes; success metrics include anti-nudge guardrails. |
| **G5. Submit** | Package all required deliverables with QA passing. | Discovery Engine, 10-slide deck, deployed MVP, and public Evidence Log accessible; `scripts/qa_check.py` passes. |

## 4. Non-Goals / Out of Scope

- **No C1 changes:** No discounts, coupons, memberships, pricing changes, referral bonuses, or changes to professional pay/management.
- **No C2 actions:** MVP must not book services, message Urban Company/professionals, or take any action on a customer account.
- **No C3 violations:** No logged-in UC scraping, no private app data, no non-public sources.
- **No fabricated evidence:** No invented interview quotes, golden labels, agreement scores, or user-test observations.
- **No bad-experience-only framing:** Do not frame the root cause simply as "customers had a bad experience" or "customers need an offer to come back."
- **No PII collection:** No booking screenshots, invoices, addresses, phone numbers, or personal documents from respondents.

## 5. Target Users

| Segment | Details |
|---|---|
| **Primary segment** | Urban renters/families in metros who used one core category once and then went quiet. |
| **Anchor context** | First completed booking in a chosen month in a core category (InstaHelp excluded). |
| **Research coverage** | 5–6 interviews; respondents completed a UC booking in last 6 months; include returners and non-returners within 90 days; cover >1 service category; record total bookings (C6). |
| **MVP user** | Any customer planning home care; MVP asks only non-PII profile inputs. |

## 6. Canonical Metric (C4/C5)

- **Metric:** Share of customers who complete another booking within 90 days of a completed booking.
- **Anchor:** Pick a month. Every customer whose first completed booking in that month was in a core category is counted once; that booking is their anchor. **Quick-service housekeeping (InstaHelp) excluded.**
- **Return:** Any later completed booking, in any category, within 90 days of the anchor booking.
- **Exclude:** Redos, warranty claims, and bookings that end in a refund.
- **Context:** ~84% of Urban Company net transaction value comes from repeat customers.

## 7. Product Scope

### 7.1 Discovery Engine

| Requirement | Acceptance criteria |
|---|---|
| Public corpus ingestion | `data/public_corpus.csv`/paste/upload; required provenance fields; PII redacted before processing; C3 guard rejects logged-in UC/app/account URLs. |
| Theme coding | Each item coded into fixed T1–T11 taxonomy with return signal, sentiment, bias flag, confidence, rationale, and optional exact quote. |
| Deterministic fallback | Engine runs without `GEMINI_API_KEY`; LLM path is optional enhancement. |
| Aggregation & bias | Theme shares, source/category stratification, return-signal cross-tab, continuity-vs-experience split, bias report with explicit limitations. |
| Golden evaluation | 20 hand-labelled rows; agreement/confusion matrix/per-theme precision-recall computed only on labelled rows; no fabricated labels. |
| Evidence log | MD/PDF/downloadable evidence log with sources/volume, agreement, failures, and >=2 corrected/rejected AI outputs. |

### 7.2 MVP — Home Care Companion

| Step | User value | Acceptance criteria |
|---|---|---|
| **1. Tell me about your home** | Capture planning context without PII. | 6 profile questions only; no name/phone/address/flat/booking screenshots; visible privacy note. |
| **2. Your next 90 days** | Make upcoming home-care needs visible. | Calendar cards show need, timing, why, confidence, public basis, source link; cap at 6; editable "add a need" input. |
| **3. Need Decider** | Route a need honestly. | Routes: `DIY`, `LOCAL_OR_NEIGHBOUR`, `UC_CATEGORY`, `WAIT_AND_WATCH`, `SEEK_IMMEDIATE_HELP`; vague input asks clarifying questions; urgent input routes to immediate help; UC_CATEGORY shows public info only, no booking CTA. |
| **4. After a service** | Capture reflection and unresolved topics. | Reflection captures open topics/unmet expectation/follow-up; downloadable personal checklist; 2-question feedback; no upload. |

### 7.3 Research & Strategy Pages

| Page | Purpose | Key output |
|---|---|---|
| **Metric Decomposition** | Break metric into customer-side stages. | D1–D6 with influenceable/publicly-measurable badges; exact metric definition. |
| **User Research** | Validate/challenge discovery. | Protocol, anonymized respondent table, synthesis, empty placeholders until real interviews. |
| **Problem Definition** | State the chosen problem. | Evolution chain, structured problem statement, explicit "not bad experience / not offer" callout. |
| **MVP Testing** | Capture real user tests. | >=3 tests with task, expected trace, observed, next iteration. |
| **Success Metrics** | Define measurement and guardrails. | Business metric, leading indicators, guardrails, tool-choice eval, anti-nudge checks. |
| **Risks** | Identify failure modes. | >=6 risks with likelihood, impact, mitigation, early warning. |
| **Deck** | Submission narrative. | 10 message-first slides, PDF export, QA checks. |

## 8. Functional Requirements

### MVP Behavior
- **FR-01:** MVP loads and completes core flows with no `GEMINI_API_KEY`.
- **FR-02:** Every Need Decider turn logs a tool trace to `outputs/tool_trace.jsonl` with route, confidence, reason, and chosen tool.
- **FR-03:** Every UC-category recommendation includes public basis/source and no booking CTA.
- **FR-04:** Vague inputs (<12 words or missing object) trigger clarifying questions and no recommendation.
- **FR-05:** Urgent safety keywords trigger `SEEK_IMMEDIATE_HELP` and no service recommendation.
- **FR-06:** Feedback logs to `outputs/mvp_feedback.jsonl`.

### Discovery/Eval
- **FR-07:** Corpus ingestion redacts PII before storage/processing and drops rows <20 chars after cleaning.
- **FR-08:** Golden-set evaluation reports agreement only over manually labelled rows.
- **FR-09:** Evidence log export works as MD and PDF downloads from Streamlit.
- **FR-10:** Discovery results export as JSON.

### QA/Compliance
- **FR-11:** `scripts/qa_check.py` checks C1/C2/C3/C4/C5/C6/C7/C8/C9/C10 assertions.
- **FR-12:** Deck PDF is `NL_UrbanCompany.pdf`, <=10 pages, <40MB, min font rules respected, no fellow name.
- **FR-13:** App contains persistent footer: "Public prototype · No bookings · No account access · Public information only".

## 9. Non-Functional Requirements

| Category | Requirement |
|---|---|
| **Privacy** | No PII collection; redact PII in ingested text; no respondent documents/screenshots. |
| **Security** | No secrets committed; `.env`/secrets ignored; API keys optional. |
| **Reliability** | Deterministic fallback when LLM unavailable; app should not crash on missing optional secrets. |
| **Accessibility** | Min body font 14px in app; readable contrast; color not sole encoding; focus outlines. |
| **Portability** | Runs locally via `streamlit run app.py`; deployable on Streamlit Cloud. |
| **Auditability** | Public source provenance, tool traces, evidence log, QA report. |

## 10. Data & AI Design

| Component | Design |
|---|---|
| **Corpus** | `data/public_corpus.csv` — public-only rows with source/date/url/class/rating/category/notes. |
| **Golden set** | `data/golden_set.csv` — 20 manually labelled rows; human labels authoritative. |
| **Interviews** | `data/interviews.csv` — 5–6 anonymized rows, R01–R06, no PII. |
| **Public reference** | `data/public_reference.csv` — public, non-UC-specific timing/need facts with source URLs. |
| **LLM** | Optional Gemini via `google-genai`; strict JSON, retry once, deterministic fallback. |
| **Taxonomy** | Fixed T1–T11; T8 control, T9 out-of-scope control, T10 excluded from metric. |
| **Traces** | `outputs/tool_trace.jsonl`, `outputs/mvp_feedback.jsonl`. |

## 11. Success Metrics

### Business / Product
- **North-star metric:** Share of customers who complete another booking within 90 days of a completed booking (C4/C5 definition).
- **Leading indicators:** Need-recognition rate, calendar usefulness, decision-confidence lift, appropriate non-UC route rate, reflection completion rate, return-intent quality (self-reported).
- **Guardrails:** No increase in unnecessary bookings; no unsafe/urgent misroutes; no C1/C2 violations; non-UC route remains available when appropriate.

### MVP Quality
- **Tool-choice quality:** Golden tasks with expected tool traces; precision/recall for route/tool choice.
- **Anti-nudge checks:** Non-UC route rate, no-need/wait-and-watch rate, 2-week "did I actually need it?" follow-up.
- **Evidence quality:** Golden-set agreement reported honestly; disagreements and corrections documented.

## 12. Risks & Mitigations

| Risk | Impact | Mitigation | Early warning |
|---|---|---|---|
| Public corpus bias over-represents complaints | Wrong problem framing | Bias report, continuity-vs-experience split, interview validation | T8 dominates despite interview contradiction |
| Fabricated/weak evidence | Submission credibility loss | No-fabrication rule; TODO placeholders; QA blockers | Missing labels/interviews/tests near deadline |
| MVP nudges unnecessary UC bookings | Trust/safety/guardrail failure | UC_CATEGORY confidence threshold, non-UC routes, anti-nudge metrics | High UC_CATEGORY rate on vague/low-confidence inputs |
| LLM unavailable or inconsistent | Demo failure | Deterministic fallback, strict JSON, model fallback | LLM errors/timeouts in logs |
| PII leakage in corpus/interviews/logs | Privacy/compliance failure | PII redaction, schema validation, QA scan | QA-12 failure or PII-like columns |
| Streamlit Cloud ephemeral storage | Lost generated artifacts | In-memory downloads; regenerate from source; commit final deliverables as needed | Missing files after redeploy |

## 13. Milestones

| Milestone | Output | Status |
|---|---|---|
| **M1 — Constraints & scaffold** | `docs/constraints.md`, project scaffold | Complete |
| **M2 — Data/engine core** | PII, ingest, taxonomy, engine, eval, opportunity, MVP logic | Complete |
| **M3 — App & pages** | Streamlit router + 10 views | Complete |
| **M4 — Deliverable drafts** | Evidence log draft, deck PDF, QA/report/docs | Complete |
| **M5 — Real evidence** | 20 golden labels, 5–6 interviews, 3 MVP tests, real public corpus | Pending |
| **M6 — Final QA & deploy** | QA 12/12, deployed URLs, final submission package | Pending |

## 14. Deliverables

| Deliverable | Format | Location / Target |
|---|---|---|
| **AI Discovery Engine** | Streamlit page + testable workflow | `views/2_Discovery_Engine.py` / deployed app |
| **10-slide deck** | PDF | `outputs/NL_UrbanCompany.pdf` / `views/10_Deck.py` |
| **Deployed AI-native MVP** | Public Streamlit app | `app.py`, `views/1_MVP.py` / Streamlit Cloud URL |
| **AI Evidence Log** | Public view + downloadable MD/PDF | `views/3_Evidence_Log.py`, `outputs/evidence_log.md`, `outputs/evidence_log.pdf` |

## 15. Acceptance Checklist

- [ ] `docs/constraints.md` respected across code, UI, outputs, and deck.
- [ ] MVP usable with no API key; no C1/C2/C3 violations.
- [ ] Real public corpus replaces illustrative-only sample.
- [ ] 20 golden rows manually labelled; agreement computed only on labelled rows.
- [ ] 5–6 anonymized interviews completed and validated.
- [ ] >=3 MVP user tests completed and documented.
- [ ] Evidence log includes sources/volume, agreement/failures, >=2 corrected AI outputs.
- [ ] Deck is 10 slides max, message-first, no fellow name, <40MB, accessible fonts.
- [ ] `python -m scripts.qa_check` passes.
- [ ] Public Streamlit/Evidence/Deck links added to `README.md`.
