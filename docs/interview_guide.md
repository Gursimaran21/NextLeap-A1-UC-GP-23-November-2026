# Interview Guide — 5–6 Anonymized User Interviews

> Respect `docs/constraints.md` (C6, C7). Do not fabricate quotes or respondents. Record only what real people tell you.

## 1. Requirements (C6) — check before you start

- [ ] **5–6 respondents**, each completed an Urban Company booking **in the last 6 months**.
- [ ] Include **both** people who booked again within 90 days (**returners**) and people who did not (**non-returners**). Aim for 3 + 3.
- [ ] Together cover **more than one service category** (e.g., AC Service + Deep Cleaning + Salon/Plumbing).
- [ ] Record **total bookings** each respondent has made (their own estimate is fine).
- [ ] Target segment: metro renters/families who used one core category once and then went quiet (non-returners especially).

**C7 — never collect:** names, phone numbers, addresses, flat numbers, booking screenshots, invoices, emails, or any personal documents. Respondents are **R01–R06** only.

## 2. Recruitment screener (2 minutes, chat/call)

Ask only these; do not record identifying answers:
1. Have you used Urban Company in the last 6 months? (must be yes)
2. Which service category was it? (need >=2 categories across your 6)
3. After that booking, did you complete any other UC booking within ~3 months? (yes → returner; no → non-returner)
4. Roughly how many UC bookings have you made in total? (number only)
5. Metro or tier-2 city? (city tier only, not city name/address)

Suggested composition:

| ID | Returner? | Category (vary) | City tier |
|---|---|---|---|
| R01 | no | AC Service | Metro |
| R02 | yes | Deep Cleaning | Metro |
| R03 | no | Plumbing | Metro/Tier 2 |
| R04 | yes | Salon | Metro |
| R05 | no | AC Service / Pest Control | Metro |
| R06 | yes or no | Deep Cleaning / Appliance Repair | Metro |

## 3. Consent + anonymity script (read verbatim)

> "This is for a student product-research project about home services. I'll record only anonymized notes — no names, numbers, addresses, screenshots, or invoices. You can skip any question or stop anytime. Is it okay if I take notes of what you say, without any personal details?"

If they offer a screenshot/invoice: **decline politely** ("I can't collect documents — just tell me in your own words").

## 4. Interview protocol (~20–25 min)

Warm-up (2 min)
1. "Tell me about the last Urban Company service you used. What prompted it?"
   - Probe: How did you find UC? Was it planned or sudden?

The anchor booking (5 min)
2. "Walk me through that booking — deciding, the visit, and right after it finished."
   - Probe: "When the professional left, what did you expect would happen next?"
   - Probe: "Did anything feel unfinished or unclear afterwards?" *(listens for T1 closure)*

The 90-day window (8 min) — **the core of the study**
3. "In the ~3 months after that service, did any other home need come up?"
   - If **yes**: "What did you do — book UC again, call someone local, ask family/neighbours, DIY, or nothing? Why that option?" *(T5 local defaults, T3 mental availability, T4 category awareness)*
   - If **no**: "Was there genuinely no need, or a need you noticed but didn't act on?" *(separates true no-need from T2 need recognition)*
4. "When a home need comes up, how do you decide what to do first?" *(T6 decision confidence)*
5. "Did you know UC offered that category? What made you think of — or not think of — UC?" *(T3/T4)*

Planning style + closing (5 min)
6. "Do you handle home maintenance planned, reactive, or avoided until urgent?" *(T7)*
7. "What would have made it easier to plan or act on the next home need?"
8. "Anything that would make you book again — or anything that would put you off?" *(listen for non-incentive reasons; do not suggest offers)*

**Moderator rules:** ask open questions; never suggest discounts/offers; never ask for documents; let silence work; note exact phrases verbatim (anonymized) for the `quote` field.

## 5. Coding each interview into `data/interviews.csv`

Columns (exact): `respondent_id,interview_date,consent,city_tier,household_type,decision_maker,last_booking_date,category,total_bookings,anchor_booking_date,returner_90d,subsequent_need,Q4_discovery,Q5_booking_reason,Q6_provider_choice,Q7_post_service,Q8_expectations,Q9_next_need,Q10_arrangement,Q11_considered_UC,Q12_alternative,Q13_return_motivation,Q14_barriers,Q15_planning,Q16_tracking_value,Q17_decision_information,Q18_usefulness,main_barrier,researcher_notes,quote,theme_code`

| Column | How to fill |
|---|---|
| `respondent_id` | R01 to R06 |
| `interview_date` | Date of interview; leave blank until recorded |
| `consent` | Consent status; leave blank until recorded |
| `city_tier` | `Metro` or `Tier 2`; no address or identifying detail |
| `household_type` | e.g., apartment / independent / family / kids / pets |
| `decision_maker` | Who decides on the service, in anonymized terms |
| `last_booking_date` | Most recent completed booking date |
| `category` | Anchor category (e.g., `AC Service`, `Deep Cleaning`, `Plumbing`, `Salon`) |
| `total_bookings` | Integer, their estimate |
| `anchor_booking_date` | Date of the anchor completed booking |
| `returner_90d` | `yes` only if another completed booking happened within 90 days (any category; redos/warranty/refunds do not count - C5). Otherwise `no`. |
| `subsequent_need` | Next home need that arose after the anchor service |
| `Q4_discovery` | How they discovered or recognised the need |
| `Q5_booking_reason` | Why they booked the anchor service |
| `Q6_provider_choice` | How they chose the provider |
| `Q7_post_service` | What happened after the service |
| `Q8_expectations` | Expectations after the service |
| `Q9_next_need` | Next need they anticipated or missed |
| `Q10_arrangement` | How the service was arranged |
| `Q11_considered_UC` | Whether Urban Company was considered when the need arose |
| `Q12_alternative` | Alternative used or considered |
| `Q13_return_motivation` | What would motivate another booking |
| `Q14_barriers` | What would prevent another booking |
| `Q15_planning` | How they plan home services |
| `Q16_tracking_value` | Value of tracking service timing |
| `Q17_decision_information` | Information needed to decide confidently |
| `Q18_usefulness` | Usefulness of planning guidance |
| `main_barrier` | Primary barrier in their own words |
| `researcher_notes` | 1–3 sentences: context, workaround, what validates/challenges engine findings. No PII. |
| `quote` | One verbatim anonymized quote that best captures their pattern |
| `theme_code` | Primary theme from the legend below |

Theme legend (pick ONE primary):
- `T1_POST_SERVICE_CLOSURE` — no clear next step after service; need faded
- `T2_NEED_RECOGNITION` — didn't recognize the next need in time
- `T3_MENTAL_AVAILABILITY` — UC not top-of-mind when need arose
- `T4_CATEGORY_AWARENESS` — didn't know UC offers that category
- `T5_LOCAL_WHATSAPP_DEFAULT` — defaulted to local/neighbour/WhatsApp/family
- `T6_DECISION_CONFIDENCE` — unsure what service / DIY vs professional
- `T7_PLANNING_SEASONALITY` — seasonal/planned need not anticipated
- `T8_EXPERIENCE_QUALITY` — service quality issue (control theme)
- `T9_PRICE_OFFER` — price/incentive expectation (control; out of scope for solution)
- `T10_REDO_REFUND` — redo/warranty/refund case (excluded from metric)
- `T11_UNCLASSIFIED` — insufficient signal

Required column order is the header above. Fill only anonymized values; leave unrecorded fields empty until the real interview is coded.

Key-field example (**structure only — replace with real interview content**):
```text
respondent_id=R01 | category=AC Service | returner_90d=no | total_bookings=1 | quote=<verbatim anonymized quote> | theme_code=T1_POST_SERVICE_CLOSURE | researcher_notes=<1-3 sentence context; no PII>
```

## 6. After all interviews

1. Save `data/interviews.csv` (UTF-8). Validate: `python -c "from src import research; print(research.load_interviews().shape)"`.
2. Update the synthesis in `views/5_User_Research.py`: which findings **validate** vs **challenge** the discovery engine (remember: real app-store data showed mostly experience complaints; interviews are where continuity signals should appear — or not).
3. Update deck slide 5 (`src/deck.py`) from "planned" to actual findings **only after interviews are done**; rebuild with `python -m src.deck`.
4. Run `python -m scripts.qa_check`.
