# Demo Script (3–5 minutes)

## Setup
- Open deployed Streamlit app (or `streamlit run app.py` locally).
- Confirm sidebar footer: “Public prototype · No bookings · No account access · Public information only”.

## 1) Problem & metric (30s)
- Open **Metric Breakdown**. Show exact 90-day repeat metric and D1–D6 decomposition.
- Call out: customer-side, no internal data, no discounts/offers.

## 2) AI Discovery Engine (60s)
- Open **Discovery Engine**. Show LLM status (live/offline fallback).
- Toggle “Use bundled illustrative sample”, click **Run engine**.
- Show: theme distribution, continuity vs experience split, bias report, top quotes.
- Open **Evidence Log**. Show agreement/golden status, confusion matrix placeholder if unlabelled, corrections, limitations.
- Download `evidence_log.md` or `discovery_results.json`.

## 3) MVP — Home Care Companion (90s)
- Open **Home Care Companion** (default).
- **Step 1:** fill profile (no PII). Save.
- **Step 2:** build 90-day calendar. Show public basis/source links and confidence. Add a custom need.
- **Step 3:** try three prompts in Need Decider:
  - “AC not cooling” → UC_CATEGORY with public reference.
  - “tap dripping” → routing with reason.
  - “something feels off in my kitchen but not sure what” → WAIT_AND_WATCH + clarifying questions.
- Point out “Tool used this turn…” chip and “why not other routes”.
- **Step 4:** enter post-service note, generate reflection checklist, download private JSON. Submit feedback.
- End screen: “Nothing here books anything.”

## 4) Decision & guardrails (45s)
- Open **Problem Definition**: show “not bad experience, not offer” callout.
- Open **Success Metrics**: business metric, leading indicators, guardrails, tool-choice golden tasks.
- Open **Risks**: 6 risks with mitigation and early warning.

## 5) Close (15s)
- Open **Deck**. Download `NL_UrbanCompany.pdf`.
- State next steps: label golden set, complete 5–6 interviews, run 3 user tests, rerun QA, deploy public links.
