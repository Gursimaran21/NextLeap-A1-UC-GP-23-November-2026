# PRD — Urban Company Home Care Companion

> **Respect `docs/constraints.md`.** This PRD defines the product, scope, and acceptance criteria for the NextLeap Urban Company Graduation Project (Nov 2026, PMF Cohort 52). The authoritative brief is `docs/ProblemStatement.txt`; if any requirement conflicts with `docs/constraints.md`, the constraint wins.

## 1. Document Control

| Field | Value |
|---|---|
| **Product** | Urban Company — Home Care Companion (customer-side prototype) |
| **Project** | NextLeap PM Fellowship Graduation Project, Nov 2026, PMF Cohort 52 |
| **Role** | Product Manager, Urban Company Consumer Growth Team (project simulation) |
| **Owner** | Fellow (name excluded from deck per C8) |
| **Status** | Draft / in build |
| **Primary docs** | `docs/ProblemStatement.txt`, `docs/brief.md`, `docs/constraints.md`, `README.md` |
| **Submission deadline** | Dec 13, 2026, 3:59:00 PM IST |

## 2. Problem Statement

### 2.1 Business context and objective

Urban Company connects customers with professionals for deep cleaning, AC servicing, plumbing, electrical repairs, salon services, and other household requirements. A customer may complete a booking, receive the service successfully, and pay — yet not return for the next household service requirement. Some customers complete another booking within 90 days; others do not.

**Business objective:** increase the percentage of customers who complete another service booking within 90 days of their initial completed booking. This is a business objective, not yet a validated customer problem.

### 2.2 Core problem to investigate

Customers who complete an Urban Company service booking may not consider the platform when another household need arises. Even after a successful previous booking, they may choose local providers, rely on friends or neighbours, try alternative platforms, or postpone the requirement. The reasons for these decisions are not yet clearly understood.

> **Key question:** Why do customers who successfully complete an Urban Company booking not necessarily return to the platform for another service within 90 days, and what customer needs or barriers influence their decision to return or choose an alternative?

The investigation must include cases where **nothing went wrong** — the root cause must not be assumed to be a bad experience or a need for offers.

### 2.3 Research objectives

| Area | Questions to answer |
|---|---|
| **A. Customer behaviour** | How do customers identify and recognise household service needs? Are services planned in advance or requested reactively? What drove the first Urban Company booking? |
| **B. Post-booking experience** | What do customers expect after a completed service? Do further household needs arise afterwards? How do they decide what to do next? |
| **C. Repeat-booking decisions** | What motivates a return? Why choose local providers, other platforms, or recommendations? What prevents consideration of Urban Company? Does a satisfactory prior experience influence the next decision? |
| **D. Segmentation** | How does behaviour differ by service category, city, household type, and booking frequency (frequent vs occasional)? |

### 2.4 Expected product opportunity

Identify a customer-centric opportunity that addresses a **validated** need and makes Urban Company more relevant when subsequent household needs arise — providing meaningful customer value while supporting the 90-day repeat-booking objective. The final opportunity is selected only after AI discovery, metric decomposition, primary research, and problem definition; it is not pre-decided.

## 3. Goals

| Goal | Description | Success signal |
|---|---|---|
| **G1. Discover** | Build an AI-powered discovery engine that codes public feedback into opportunity themes and surfaces evidence quality/bias. | Engine runs on public corpus; outputs T1–T11 themes, bias report, golden-set evaluation, evidence log; goes beyond sentiment/summarisation. |
| **G2. Define** | Decompose the business metric, validate with primary research, and define a clear customer-side problem. | D1–D6 decomposition with measurable indicators, 5–6 anonymized interviews, 7-field problem definition grounded in evidence. |
| **G3. Build** | Ship a functional, publicly testable MVP that works from customer input and public information only. | Streamlit MVP deployed; 4-step flow usable without API key; no booking/account actions. |
| **G4. Validate** | Test the MVP with target users and define success/guardrails/AI-quality metrics. | >=3 user tests with observations and iteration changes; metrics framework includes leading, guardrail, and AI-performance measures. |
| **G5. Submit** | Package all required deliverables with QA passing. | Discovery Engine, 10-slide deck, deployed MVP, and public Evidence Log accessible; `scripts/qa_check.py` passes. |

### 3.1 Requirement traceability (from `docs/ProblemStatement.txt`)

| Requirement | Covered in | Deliverable |
|---|---|---|
| **R1** AI-powered discovery engine | §7.1, §10 | D1 Discovery Engine, D4 Evidence Log, deck slide on workflow |
| **R2** Business metric decomposition | §6, §7.3 | Deck (metric decomposition) |
| **R3** User research validation | §5, §7.3 | Deck (user research) |
| **R4** Problem definition | §7.4 | Deck (target segment, root cause, problem) |
| **R5** Deployed AI-native MVP | §7.2 | D3 Deployed MVP |
| **R6** MVP user testing | §7.3, §11 | Deck (MVP and testing) |
| **R7** Success metrics | §11 | Deck (success metrics) |
| **R8** Risks and mitigations | §12 | Deck (risks and limitations) |

## 4. Non-Goals / Out of Scope

- **No C1 changes:** No discounts, coupons, memberships, pricing changes, referral bonuses, or changes to professional pay/management.
- **No C2 actions:** MVP must not book services, message Urban Company/professionals, or take any action on a customer account.
- **No C3 violations:** No logged-in UC scraping, no private app data, no non-public sources.
- **No fabricated evidence:** No invented interview quotes, golden labels, agreement scores, or user-test observations.
- **No bad-experience-only framing:** Do not frame the root cause simply as "customers had a bad experience" or "customers need an offer to come back." Investigate non-return after a successful booking.
- **No artificial demand:** Address genuine customer needs; do not encourage unnecessary service bookings or misleading recommendations.
- **No PII collection:** No booking screenshots, invoices, addresses, phone numbers, or personal documents from respondents.

## 5. Target Users and Segmentation

| Segment | Details |
|---|---|
| **Primary segment** | Urban renters/families in metros who used one core category once and then went quiet. |
| **Anchor context** | First completed booking in a chosen month in a core category (InstaHelp excluded). |
| **Research coverage** | 5–6 interviews; respondents completed a UC booking in last 6 months; include returners and non-returners within 90 days; cover >1 service category; record total bookings (C6). |
| **Segmentation lenses** | Service category, city/tier, household type, and booking frequency (frequent vs occasional). treated as hypotheses to validate, not established facts. |
| **MVP user** | Any customer planning home care; MVP asks only non-PII profile inputs. |

## 6. Canonical Metric (C4/C5)

- **Metric:** Share of customers who complete another booking within 90 days of a completed booking.
- **Anchor:** Pick a month. Every customer whose **first completed booking in that month** was in a **core category** is counted once; that booking is their anchor. **Quick-service housekeeping (InstaHelp) excluded.**
- **Core categories:** As configured in `src/config.py` (Deep Cleaning, AC Service, Plumbing, Salon, Pest Control, Appliance Repair).
- **Return:** Any later completed booking, **in any category**, within 90 days of the anchor booking.
- **Exclude:** Redos, warranty claims, and bookings that end in a refund.
- **Context:** ~84% of Urban Company net transaction value comes from repeat customers.

## 7. Product Scope

### 7.1 Discovery Engine (R1)

| Requirement | Acceptance criteria |
|---|---|
| Eligible public sources | Apple App Store reviews, Google Play reviews, Trustpilot/consumer forums, Reddit (Indian city/household communities), public social conversations, YouTube comments, UC public shareholder letters, public earnings-call transcripts, and other public home-service conversations. No logged-in/private UC data (C3). |
| Current corpus status | `data/public_corpus.csv` currently contains real App Store (India) reviews only; single-source, complaint-heavy limitation documented in `docs/sources.md`. Other eligible sources remain future work, not claimed as analysed. |
| Public corpus ingestion | CSV/paste/upload with `source_url`, `source_class`, `access_date` provenance; PII redacted before processing; C3 guard rejects logged-in UC/app/account URLs. |
| Theme coding | Each item coded into fixed T1–T11 taxonomy with return signal, sentiment, bias flag, confidence, rationale, and optional exact quote. Engine identifies post-service expectations, need recognition/planning, return/non-return reasons, local/recommendation/alternative preferences, frustrations, category/city/household differences, and opportunity areas — **beyond sentiment analysis and review summarisation**. |
| Quantification & comparison | Theme shares, source/category stratification, return-signal cross-tab, continuity-vs-experience split, comparison of opportunity areas, evidence-backed insights. |
| Deterministic fallback | Engine runs without `GEMINI_API_KEY`; LLM path is optional enhancement. |
| Golden evaluation | ~20 hand-labelled rows; AI classifications compared to manual labels; agreement, failures, and per-theme precision/recall computed only on labelled rows; no fabricated labels. |
| Bias handling | Explicit report of public-review bias and the missing voice of customers who simply never return; corrections/rejections documented with reasons. |
| Evidence log | MD/PDF/downloadable evidence log with sources/volume, agreement, failures, and **2–3** rejected/corrected AI outputs explained. |
| Demo isolation | Sample/demo runs write to `discovery_results_sample.json` and never overwrite canonical real-corpus evidence. |

### 7.2 MVP — Home Care Companion (R5)

**Selection rule:** the MVP format and scope are chosen only after discovery, metric decomposition, and primary research. Acceptable formats: AI-powered feature, workflow, agent, or standalone customer experience. Current selected format: a customer-side Streamlit experience using customer-provided and public information only.

| Requirement | Acceptance criteria |
|---|---|
| Addresses validated problem | Every flow traces to the validated problem definition (§7.4), not to an assumed bad experience or incentive need. |
| Functional & public | Deployed to production, accessible to mentors for real-task testing; usable without an API key. |
| Customer-side only | Uses customer input and public information; no booking, messaging, account actions, scraping, pricing, or professional-side changes (C1/C2/C3). |

| Step | User value | Acceptance criteria |
|---|---|---|
| **1. Tell me about your home** | Capture planning context without PII. | 6 profile questions only; no name/phone/address/flat/booking screenshots; visible privacy note. |
| **2. Your next 90 days** | Make upcoming home-care needs visible. | Calendar cards show need, timing, why, confidence, public basis, source link; cap at 6; editable "add a need" input. |
| **3. Need Decider** | Route a need honestly. | Routes: `DIY`, `LOCAL_OR_NEIGHBOUR`, `UC_CATEGORY`, `WAIT_AND_WATCH`, `SEEK_IMMEDIATE_HELP`; vague input asks clarifying questions; urgent input routes to immediate help; UC_CATEGORY shows public info only, no booking CTA. |
| **4. After a service** | Capture reflection and unresolved topics. | Reflection captures open topics/unmet expectation/follow-up; downloadable personal checklist; 2-question feedback; no upload. |

### 7.3 Research & Strategy Pages

| Page | Purpose | Key output |
|---|---|---|
| **Metric Decomposition (R2)** | Break the metric into customer-side stages. | Explicit chain **Business Metric → Product Outcomes → Customer Behaviours → Measurable Indicators** (D1–D6 below); influenceable/publicly-measurable badges; exact metric definition. Used alongside discovery findings to prioritise opportunities. |
| **User Research (R3)** | Validate/challenge discovery with interviews. | Interview questionnaire covering the 9 areas below; anonymized respondent profiles; repeat vs non-repeat comparison; common patterns; insights that validate/challenge AI findings. Empty placeholders until real interviews exist. |
| **Problem Definition (R4)** | State the chosen problem from evidence. | Evolution chain, 7 required fields (§7.4), explicit "not bad experience / not offer" callout. |
| **MVP Testing (R6)** | Capture real user tests. | Methodology, >=3 tasks with expected trace, observations, feedback, what worked/did not work, issues, and next-iteration changes. |
| **Success Metrics (R7)** | Define measurement, guardrails, AI quality. | Metrics framework (§11); business metric, leading indicators, guardrails, AI-performance checks. |
| **Risks (R8)** | Identify failure modes. | >=6 risks with likelihood, severity, impact, mitigation, early warning. |
| **Deck** | Submission narrative. | 10 message-first slides covering the 9 required topics (§14); PDF export, QA checks. |

**D1–D6 decomposition:**

| Stage | Customer behaviour | Product outcome | Measurable indicator |
|---|---|---|---|
| D1 Need incidence | Did another need actually arise in 90 days? | Anticipate genuine need | Public cadence/seasonality references (not directly observable) |
| D2 Need recognition | Did the customer notice the need in time? | Timely need recognition | Interview recall of missed/delayed maintenance |
| D3 Mental availability | Did they think of Urban Company? | Continuity/top-of-mind | Interview consideration/recall questions |
| D4 Category consideration | Did they know UC offered that service? | Category clarity | Interview awareness questions; public "does UC do X?" posts |
| D5 Choice vs alternatives | Did they choose UC over local/DIY/other? | Confident choice | Interview alternatives used; public comparison posts |
| D6 Frictionless completion | Could they complete the booking without friction? | Frictionless completion | Public app reviews on booking/payment/support friction (used carefully) |

**Interview areas (R3):** (1) initial booking decision, (2) how they discovered UC, (3) what happened after the service, (4) expectations, (5) additional needs afterwards, (6) how they handled subsequent needs, (7) whether they considered UC again, (8) motivators/barriers to return, (9) whether services are planned, reactive, or avoided.

### 7.4 Problem Definition Fields (R4)

| Field | Evidence source | Status |
|---|---|---|
| Target user segment | Metric + discovery + interviews | Hypothesis in §5; validate in interviews |
| Customer journey scenario | Interview narratives | Pending real interviews |
| Product outcome to influence | D1–D6 decomposition | Defined (§7.3) |
| Root cause | Discovery themes + interview comparison | Pending; must not default to "bad experience" |
| Existing workarounds | Interviews/public alternatives | Pending real interviews |
| User value created | Validated need | Pending validation |
| Business value created | 90-day repeat metric | Defined by business objective |

**Required evolution:** Business Metric → Product Outcomes → AI Discovery → Primary Research → Problem Definition. Explain explicitly how interviews validated or challenged AI discovery findings.

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
- **FR-10:** Discovery results export as JSON; demo/sample runs export to a separate file.

### QA/Compliance
- **FR-11:** `scripts/qa_check.py` checks C1/C2/C3/C4/C5/C6/C7/C8/C9/C10 assertions.
- **FR-12:** Deck PDF is `NL_UrbanCompany.pdf`, <=10 slides, <40MB, min font rules respected, no fellow name.
- **FR-13:** App contains persistent footer: "Public prototype · No bookings · No account access · Public information only".

## 9. Non-Functional Requirements

| Category | Requirement |
|---|---|
| **Privacy** | No PII collection; redact PII in ingested text; no respondent documents/screenshots. |
| **Security** | No secrets committed; `.env`/secrets ignored; API keys optional. |
| **Reliability** | Deterministic fallback when LLM unavailable; app should not crash on missing optional secrets. |
| **Accessibility** | Min body font 14px in app; readable contrast; colour not sole encoding; focus outlines. |
| **Portability** | Runs locally via `streamlit run app.py`; deployable on Streamlit Cloud. |
| **Auditability** | Public source provenance, tool traces, evidence log, QA report. |

## 10. Data & AI Design

| Component | Design |
|---|---|
| **Corpus** | `data/public_corpus.csv` — public-only rows with source/date/url/class/rating/category/notes. Currently App Store (India) only; see §7.1 and `docs/sources.md`. |
| **Golden set** | `data/golden_set.csv` — ~20 manually labelled rows; human labels authoritative. |
| **Interviews** | `data/interviews.csv` — 5–6 anonymized rows, R01–R06, no PII. |
| **Public reference** | `data/public_reference.csv` — public, non-UC-specific timing/need facts with source URLs. |
| **LLM** | Optional Gemini via `google-genai`; strict JSON, retry once, deterministic fallback. |
| **Taxonomy** | Fixed T1–T11; T8 control, T9 out-of-scope control, T10 excluded from metric. |
| **Traces** | `outputs/tool_trace.jsonl`, `outputs/mvp_feedback.jsonl`. |

## 11. Success Metrics (R7)

Every metric in the framework is documented with: **name, definition, measurement method, target/expected direction, and rationale**.

### A. Business / Product
- **North-star (primary business metric):** Share of customers who complete another booking within 90 days of their anchor booking (C4/C5 definition).
- **Leading indicators:** Need-recognition rate, calendar usefulness, decision-confidence lift, appropriate non-UC route rate, reflection completion rate, adoption/continued usage, return-intent quality (self-reported).
- **Guardrails:** No increase in unnecessary bookings; no misleading recommendations; customer trust/satisfaction maintained; no unsafe/urgent misroutes; no C1/C2 violations; non-UC route remains available when appropriate.

### B. AI performance
- Accuracy of AI-generated recommendations against manually labelled golden examples.
- Correct tool/route selection, including choosing the right tool at the right moment (tool-trace evaluation).
- Recognition of cases where **no action or recommendation is required** (WAIT_AND_WATCH / clarifying question).
- Frequency of incorrect or unnecessary recommendations, reported explicitly.

### C. Evidence quality
- Golden-set agreement reported honestly; disagreements, failures, and 2–3 corrections documented with reasons.
- Anti-nudge checks: non-UC route rate, no-need rate, two-week "did I actually need it?" follow-up where feasible.

## 12. Risks & Mitigations (R8)

| Risk | Impact | Likelihood | Severity | Mitigation | Early warning |
|---|---|---|---|---|---|
| Public corpus bias over-represents complaints | Wrong problem framing | High | High | Bias report, continuity-vs-experience split, interview validation | T8 dominates despite interview contradiction |
| Silent non-returners absent from public data | False confidence in themes | High | High | Explicit limitation; interviews include non-returners | Findings based only on reviewers |
| Fabricated/weak evidence | Submission credibility loss | Medium | High | No-fabrication rule; TODO placeholders; QA blockers | Missing labels/interviews/tests near deadline |
| Incorrect or unnecessary AI recommendations | Trust/safety failure | Medium | High | Golden-set eval, tool-choice checks, confidence thresholds, no-action routes | High UC_CATEGORY rate on vague inputs |
| Incomplete or outdated public information | Misleading timing/category guidance | Medium | Medium | Source links, dates, confidence labels, public-only reference | Stale or unsourced card content |
| MVP nudges unnecessary UC bookings | Guardrail failure | Medium | High | Non-UC routes, anti-nudge metrics, no booking CTA | Rising booking-intent language in traces |
| Low adoption / poor UX | No real task completion | Medium | Medium | 3 user tests, task-based iteration, simple flow | Users abandon before step 3 |
| Over-reliance on AI | Unchecked errors reach users | Medium | Medium | Deterministic fallback, transparent rationale, human-labelled validation | Team accepts AI output without review |
| PII leakage in corpus/interviews/logs | Privacy/compliance failure | Low | High | PII redaction, schema validation, QA scan | QA-12 failure or PII-like columns |
| Streamlit Cloud ephemeral storage | Lost generated artifacts | Medium | Medium | In-memory downloads; regenerate from source; commit final deliverables | Missing files after redeploy |
| Category/city behaviour differences | Segment hypothesis invalid | Medium | Medium | Segment across category/city/household/frequency in interviews | One category dominates all findings |

## 13. Milestones

| Milestone | Output | Status |
|---|---|---|
| **M1 — Constraints & scaffold** | `docs/constraints.md`, project scaffold | Complete |
| **M2 — Data/engine core** | PII, ingest, taxonomy, engine, eval, opportunity, MVP logic | Complete |
| **M3 — App & pages** | Streamlit router + 10 views | Complete |
| **M4 — Deliverable drafts** | Evidence log draft, deck PDF, QA/report/docs | Complete |
| **M5 — Real evidence** | ~20 golden labels, 5–6 interviews, 3 MVP tests, real public corpus | Pending (corpus complete; labels/interviews/tests pending) |
| **M6 — Final QA & deploy** | QA 12/12, deployed URLs, final submission package | Pending |

## 14. Deliverables

| Deliverable | Required content (from `docs/ProblemStatement.txt`) | Location / Target |
|---|---|---|
| **D1 — AI Discovery Engine** | Public link where the workflow can be tested; **one slide** explaining how the workflow operates. | `views/2_Discovery_Engine.py` / deployed app; deck slide |
| **D2 — Final presentation** | PDF, **max 10 slides (title slide counts)**: (1) metric decomposition, (2) engine and findings, (3) user research, (4) target segment, (5) root cause/problem, (6) solution rationale, (7) MVP and testing, (8) success metrics, (9) risks/limitations. Message-first titles, min font 14pt, no fellow name, <40MB. | `outputs/NL_UrbanCompany.pdf` / `views/10_Deck.py` |
| **D3 — Deployed AI-native MVP** | Publicly accessible link; functional prototype/workflow/agent; another person can interact and test real tasks. | `app.py`, `views/1_MVP.py` / Streamlit Cloud URL |
| **D4 — AI Evidence Log** | One document with view access for anyone with the link: (1) sources analysed, (2) volume of data, (3) ~20 manually labelled examples, (4) AI vs manual comparison, (5) agreement rate and failures, (6) **2–3** rejected/corrected outputs with explanations. | `views/3_Evidence_Log.py`, `outputs/evidence_log.md`, `outputs/evidence_log.pdf` |

## 15. Execution Principles & Framework

Evidence-first PM approach (from `docs/ProblemStatement.txt`, Section 4):

1. Do not assume the customer problem before analysing the evidence.
2. Do not select the MVP before completing primary research.
3. Distinguish customer problems from business objectives.
4. Support product decisions with evidence from discovery and interviews.
5. Validate AI-generated insights instead of accepting them blindly.
6. Focus on meaningful customer value rather than artificially increasing bookings.
7. Ensure the final MVP is functional, deployed, and testable.

**Framework:** Business Objective → Business Metric Decomposition → AI-Powered Discovery Engine → Opportunity Identification → Primary Customer Research → Validated Problem Definition → AI-Native MVP Development → User Testing and Iteration → Success Metrics → Risk Assessment and Final Presentation.

**Final goal:** identify a genuine customer problem affecting repeat-booking behaviour, build an AI-native experience to address it, and show through research and testing how it creates customer value while supporting the 90-day repeat-booking objective.

## 16. Acceptance Checklist

- [ ] `docs/constraints.md` respected across code, UI, outputs, and deck.
- [ ] MVP usable with no API key; no C1/C2/C3 violations.
- [ ] Real public corpus replaces illustrative-only sample; source limits stated honestly.
- [ ] Discovery engine covers R1 outputs and goes beyond sentiment/summarisation.
- [ ] Metric decomposition shows Business Metric → Product Outcomes → Customer Behaviours → Measurable Indicators.
- [ ] ~20 golden rows manually labelled; agreement computed only on labelled rows.
- [ ] 5–6 anonymized interviews cover all 9 interview areas and both returner groups.
- [ ] Problem definition covers all 7 fields and the required evolution chain.
- [ ] >=3 MVP user tests completed, documented, and fed into iteration.
- [ ] Success metrics include leading, guardrail, and AI-performance measures with the 5-field framework.
- [ ] Evidence log includes sources/volume, agreement/failures, 2–3 corrections with reasons.
- [ ] Deck is 10 slides max (title counts), covers all 9 required topics, message-first, no fellow name, <40MB.
- [ ] `python -m scripts.qa_check` passes.
- [ ] Public Streamlit/Evidence/Deck links added to `README.md`.
