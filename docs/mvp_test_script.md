# MVP Test Script — 3 Real User Tests

> Respect `docs/constraints.md` (C2, C6, C7). Record only real observations — never invent results. The MVP must not book, message, or act on any account; if a participant asks it to book, note that as an observation, not a feature request to implement.

## 1. Setup (5 min before each session)

- App: deployed Streamlit URL (or locally `streamlit run app.py`). Open the **MVP** page (root).
- Participant: 3 users from the target segment who completed a UC booking (test plan calls for return users; include a non-returner if possible to stress-test the continuity hypothesis).
- Privacy: no names/numbers/addresses recorded; label participants **R_T1, R_T2, R_T3**. No screenshots of their UC account/invoices.
- Ask them to **think aloud**. You observe; do not guide unless they are stuck >60s (note the intervention).
- Traces are written to `outputs/tool_trace.jsonl` on the machine running the app — keep it for evidence.

## 2. Moderator intro (read verbatim)

> "This is a public prototype about planning home care. It cannot book anything or access any account, and it only uses public information. Please try these tasks as if they were your own home needs, and tell me what you're thinking as you go. There are no wrong answers — I'm testing the app, not you."

## 3. Tasks (expected routes verified against `src/mvp.py` on 2026-11-23)

### T1 — Profile, household history + 90-day plan (~5 min)
- Ask: "Fill in the home profile. In the optional history, set last AC servicing to 4-6 months, last deep cleaning to 7-12 months, plumbing issue to None, and add Bathroom cleaning as an upcoming need. Then build your plan and pick the cue that feels most real for your home."
- **Expected trace:** `build_calendar` → `summarise_plan` (if used) → `show_public_info`.
- Observe: Are the profile and history questions comfortable (no PII)? Do plan cards' **public basis + source links** build trust? Is the relative timing believable? Does any item feel like a made-up need? Can the participant download the Markdown plan and `.ics` reminders?

### T2 — Vague need (~3 min)
- Ask them to type exactly: `something feels off in my kitchen but not sure what`
- **Expected:** `ask_clarifying_question`; **no recommendation** (route shows WAIT_AND_WATCH, confidence ~0.2, 2 clarifying questions).
- Then ask them to answer the clarifying questions in their own words and resubmit.
- Observe: Do they understand why nothing was recommended? Do the questions feel helpful or annoying?

### T3 — Clear need (~3 min)
- Ask them to type exactly: `AC not cooling since two days`
- **Expected:** `route_need` → **UC_CATEGORY** (confidence ~0.95) with public category info only; `show_public_info`.
- Observe: Is the "why not other routes" explanation clear? **Confirm there is no booking button/CTA.** Does public-only info feel useful or pointless?
- Repeat with: `tap dripping in the bathroom` → expected **UC_CATEGORY** (Plumbing, ~0.7).

### T4 — Safety check (~2 min)
- Ask them to type exactly: `I smell gas near the stove`
- **Expected:** **SEEK_IMMEDIATE_HELP** (confidence 0.99), no service recommendation.
- Observe: Is the safety message clear and calm? Would they trust it?

### T5 — Post-service reflection (~3 min)
- Ask: "Think of your last completed service. Type what went well and anything still open, then download your checklist."
- **Expected trace:** `capture_reflection` → private checklist download (no upload).
- Observe: Are open topics captured correctly? Is the download understandable? Any privacy concern?

### T6 — Explicit no-need (~2 min)
- Ask: "Try the 'No service needed right now' button in Step 3, and mark AC servicing as not needed in Step 2 history."
- **Expected trace:** `route_need` with route `NO_ACTION`; plan card status `Not needed`.
- Observe: Does the participant understand that no recommendation or reminder was added? Does this increase or reduce trust?

### Optional probe — known edge case
- Input: `AC not cooling since yesterday and I already cleaned the filter`
- Current behavior: routes **DIY** (~0.78) because maintenance keywords dominate. Record whether the participant finds this appropriate or expects professional help — this is a candidate iteration item.

## 4. Observation record (copy per participant)

```text
Participant: R_T_ (returner? yes/no; category; total bookings)
Date:
T1 calendar: success? / time / confusion / quote:
T2 vague:    success? / time / confusion / quote:
T3 clear:    success? / time / confusion / quote:
T4 safety:   success? / time / confusion / quote:
T5 reflect:  success? / time / confusion / quote:
Trust concerns:
Felt nudged toward unnecessary services? (yes/no + why)
Top friction point:
```

## 5. Debrief (3 min)

1. "Was this useful for your real home situation? Which part?"
2. "Did any suggestion feel like a sales push? Which?"
3. "Two weeks from now, how would you check whether a suggested need was real?" *(feeds the anti-nudge follow-up guardrail)*
4. "What one change would make you use this again?"

## 6. After the 3 sessions

1. Fill the three test cards in `views/7_MVP_Testing.py` (`observed`, `change_next_iteration`) with **real observations**; replace `R_T1 (placeholder)` labels with anonymized real descriptors.
2. Copy relevant trace lines from `outputs/tool_trace.jsonl` into the evidence notes (they contain no PII — only input lengths/hashes).
3. Pick the **top 2 friction points** → concrete next-iteration changes; update deck slide 9 (`src/deck.py`) from "planned" to actual results, rebuild: `python -m src.deck`.
4. Run `python -m scripts.qa_check`.
