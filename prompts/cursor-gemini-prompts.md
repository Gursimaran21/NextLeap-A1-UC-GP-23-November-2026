# Cursor + Gemini Prompt Pack — Urban Company Graduation Project

Use in order. **Every prompt must begin with:** `Respect docs/constraints.md.`  
Never fabricate golden labels, interviews, user-test observations, or private data.

---

## P0 — Lock the constraints before any code

```text
You are my senior AI product engineer. Project: "Urban Company — Graduation Project Nov 2026 (NextLeap PMF Cohort 52)".

Read the brief I paste below and create ONLY docs/constraints.md first. Do not write any code yet.

constraints.md must contain:
1. A numbered list C1..C10 exactly as in the table I give you below, each with a one-line "how it will be enforced in code" note.
2. A "Forbidden phrases / patterns" list: any mention of discount, coupon, promo, cashback, membership, free trial, price change, professional pay, professional management, "bad experience" as a root cause, "offer to come back".
3. A "Metric definition" block: anchor = first completed booking in a chosen month in a core category, InstaHelp excluded; return = any later completed booking in ANY category within 90 days; redos, warranty, refunded bookings do not count; 84% of NTV from repeat customers.
4. A "QA assertions" block listing automated checks the final app must pass.
5. A rule: EVERY later prompt must begin with "Respect docs/constraints.md".

CONSTRAINTS TABLE:
C1 no discounts/coupons/memberships/pricing/pro changes; C2 MVP cannot book/message/act on account; C3 public info only, no scraping logged-in UC; C4 exact anchor definition; C5 exact 90-day return definition; C6 5-6 interviews, both returners and non-returners, >1 category, record total bookings; C7 no screenshots/invoices/addresses/phones/docs from respondents; C8 deck 10 slides max, no fellow name, message-first titles, font >=14pt, <40MB; C9 all deliverables in Streamlit; C10 evidence log public view link + downloadable doc.

BRIEF:
[paste the full graduation project brief here]

Show me the file when done.
```

## P1 — Scaffold without overwriting

```text
Respect docs/constraints.md.

Scaffold the project IN THE CURRENT FOLDER (no nested subfolder, do not overwrite existing files).

Create: app.py, views/, src/, data/, outputs/, docs/, prompts/, scripts/, .streamlit/, requirements.txt, requirements-cloud.txt, .env.example, .gitignore, README.md (placeholder), and the file tree I specified:
- views/: 1_MVP.py, 2_Discovery_Engine.py, 3_Evidence_Log.py, 4_Metric_Decomposition.py, 5_User_Research.py, 6_Problem_Definition.py, 7_MVP_Testing.py, 8_Success_Metrics.py, 9_Risks.py, 10_Deck.py
- src/: config.py, pii.py, llm.py, ingest.py, taxonomy.py, engine.py, eval.py, opportunity.py, mvp.py, research.py, deck.py, export.py, qa.py
- data/: public_corpus.csv, golden_set.csv, interviews.csv, public_reference.csv (headers only for now)
- docs/: sources.md, methodology.md, demo_script.md, deploy_streamlit_cloud.md, qa_report.md (placeholders)

Stack: Python 3.11, streamlit>=1.39, pandas, scikit-learn, reportlab, python-dotenv, google-genai (optional), altair.
requirements-cloud.txt = requirements.txt plus google-genai.
.env.example: GEMINI_API_KEY=, GEMINI_MODEL=gemini-2.5-flash, comments explaining offline fallback.
.streamlit/config.toml: theme primaryColor "#0B6E4F", backgroundColor "#FFFFFF", sidebarBackgroundColor "#F3F6F5".
.gitignore: .env, .streamlit/secrets.toml, __pycache__, outputs/*.pdf.

Show the tree.
```

### Revised P1 prompt (paste this into Cursor/Gemini)

```text
Respect docs/constraints.md. Brief context: @docs/brief.md.

Scaffold the project IN THE CURRENT FOLDER (no nested subfolder). Do NOT overwrite existing files. Keep existing docs/brief.md and docs/constraints.md.

Create only missing files/folders:
- app.py (placeholder Streamlit entry; will be replaced in P8)
- views/: 1_MVP.py, 2_Discovery_Engine.py, 3_Evidence_Log.py, 4_Metric_Decomposition.py, 5_User_Research.py, 6_Problem_Definition.py, 7_MVP_Testing.py, 8_Success_Metrics.py, 9_Risks.py, 10_Deck.py
  Each view file: a minimal placeholder with `import streamlit as st` and `st.title("...")` or `def render(): ...` stub.
- src/: __init__.py, config.py, pii.py, llm.py, ingest.py, taxonomy.py, engine.py, eval.py, opportunity.py, mvp.py, research.py, deck.py, export.py
- scripts/: qa_check.py (placeholder with `print("QA placeholder")`)
- data/ CSVs with HEADERS ONLY (no fake data rows):
  - public_corpus.csv: item_id,source,source_class,source_url,access_date,text,rating,city,category,return_signal_hint,is_illustrative
  - golden_set.csv: item_id,text,human_primary_theme,human_return_signal,human_note
  - interviews.csv: respondent_id,category,returner_90d,total_bookings,city_tier,household_type,booking_last_6_months,interview_date,key_quote,need_timing,workaround,root_cause_signal
  - public_reference.csv: need,trigger,typical_timing_days,public_basis,source_url,source_class
- outputs/: .gitkeep
- docs/: sources.md, methodology.md, demo_script.md, deploy_streamlit_cloud.md, qa_report.md (placeholders; do not overwrite existing brief/constraints)
- prompts/: cursor-gemini-prompts.md (placeholder)
- .streamlit/config.toml
- requirements.txt, requirements-cloud.txt, .env.example, .gitignore, README.md (placeholder)

Stack: Python 3.11, streamlit>=1.39, pandas, scikit-learn, reportlab, pypdf, python-dotenv, altair. google-genai optional.

requirements.txt:
  streamlit>=1.39
  pandas
  scikit-learn
  reportlab
  pypdf
  python-dotenv
  altair

requirements-cloud.txt:
  -r requirements.txt
  google-genai

.env.example:
  # LLM (optional). Empty GEMINI_API_KEY => deterministic offline fallback.
  GEMINI_API_KEY=
  GEMINI_MODEL=gemini-2.5-flash

.streamlit/config.toml:
  [theme]
  primaryColor="#0B6E4F"
  backgroundColor="#FFFFFF"
  secondaryBackgroundColor="#F3F6F5"
  textColor="#12212B"

.gitignore must include: .env, .streamlit/secrets.toml, __pycache__/, *.pyc, .venv/, .pytest_cache/, .DS_Store, outputs/*.pdf, outputs/*.md, outputs/*.json, outputs/*.jsonl, data/raw/.

After creating, show the full tree and confirm no existing file was overwritten.
```

## P2 — Config: metric rules, taxonomy, palette, segments

```text
Respect docs/constraints.md. Create src/config.py. No secrets. Type hints, pathlib, from __future__ import annotations.

1) PATHS: ROOT, DATA, OUTPUTS, DOCS, CORPUS=data/public_corpus.csv, GOLDEN=data/golden_set.csv, INTERVIEWS=data/interviews.csv, REFERENCE=data/public_reference.csv, DISCOVERY_JSON, EVIDENCE_MD, EVIDENCE_PDF, DECK_PDF, TOOL_TRACE=outputs/tool_trace.jsonl, MVP_FEEDBACK=outputs/mvp_feedback.jsonl. ensure_dirs().

2) METRIC CONSTANTS: METRIC_NAME, ANCHOR_MONTH="2026-08", WINDOW_DAYS=90, EXCLUDED_CATEGORIES=["InstaHelp","instahelp","quick-service housekeeping"], EXCLUDED_OUTCOMES=["redo","warranty","refund","refunded"], CORE_CATEGORIES=["Deep Cleaning","AC Service","Plumbing","Salon","Pest Control","Appliance Repair"], REPEAT_NTV_PCT=84.

3) THEME LEGEND (opportunity codes) — exactly these, with one-line meanings and keyword hints:
   T1_POST_SERVICE_CLOSURE, T2_NEED_RECOGNITION, T3_MENTAL_AVAILABILITY,
   T4_CATEGORY_AWARENESS, T5_LOCAL_WHATSAPP_DEFAULT, T6_DECISION_CONFIDENCE,
   T7_PLANNING_SEASONALITY, T8_EXPERIENCE_QUALITY (control),
   T9_PRICE_OFFER (control, out of scope), T10_REDO_REFUND (excluded from metric),
   T11_UNCLASSIFIED.
   Add BIAS_FLAGS = ["bad_experience_overrepresented","silent_nonreturner_proxy","none"].
   Add RETURN_SIGNALS = ["returned","did_not_return","unclear"].

4) SEGMENT: SEGMENT_NAME = "Urban renters/families in metros who used one core category once and stopped"; SEGMENT_NOTES dict.

5) DECOMPOSITION stages D1..D6 (need incidence, need recognition, mental availability, category consideration, choice vs alternatives, frictionless completion) with "influenceable": bool and "publicly_measurable": bool.

6) PALETTE: COLOR blind-safe: ink "#12212B", teal "#0B6E4F", amber "#E08A00", blue "#2C6EAA", grey "#6B7A83", light "#F3F6F5". No red/green-only encoding; always pair colour with a label or pattern.

7) LIMITS: GOLDEN_N=20, INTERVIEW_MIN=5, INTERVIEW_MAX=6, DECK_MAX=10, MIN_FONT_PT=14, MAX_PDF_MB=40, MIN_CORPUS=150.

Show me the file.
```

### Revised P2 prompt

```text
Respect docs/constraints.md. Brief context: @docs/brief.md.

Create/replace src/config.py only. No secrets. Use `from __future__ import annotations`, type hints, and pathlib.

1) PATHS
- ROOT = Path(__file__).resolve().parents[1]
- DATA_DIR, OUTPUTS_DIR, DOCS_DIR
- CORPUS = DATA_DIR / "public_corpus.csv"
- GOLDEN = DATA_DIR / "golden_set.csv"
- INTERVIEWS = DATA_DIR / "interviews.csv"
- REFERENCE = DATA_DIR / "public_reference.csv"
- DISCOVERY_JSON = OUTPUTS_DIR / "discovery_results.json"
- EVIDENCE_MD = OUTPUTS_DIR / "evidence_log.md"
- EVIDENCE_PDF = OUTPUTS_DIR / "evidence_log.pdf"
- DECK_PDF = OUTPUTS_DIR / "NL_UrbanCompany.pdf"
- TOOL_TRACE = OUTPUTS_DIR / "tool_trace.jsonl"
- MVP_FEEDBACK = OUTPUTS_DIR / "mvp_feedback.jsonl"
- def ensure_dirs() -> None: create DATA_DIR, OUTPUTS_DIR, DOCS_DIR, OUTPUTS_DIR parents as needed.

2) METRIC CONSTANTS (C4/C5)
- METRIC_NAME = "Share of customers who complete another booking within 90 days of a completed booking"
- ANCHOR_MONTH = "2026-08"  # chosen analysis month; document rationale in deck/docs
- WINDOW_DAYS = 90
- EXCLUDED_CATEGORIES = ["InstaHelp", "instahelp", "quick-service housekeeping"]
- EXCLUDED_OUTCOMES = ["redo", "warranty", "refund", "refunded"]
- CORE_CATEGORIES = ["Deep Cleaning", "AC Service", "Plumbing", "Salon", "Pest Control", "Appliance Repair"]
- REPEAT_NTV_PCT = 84
- METRIC_DEFINITION: a multi-line string containing the exact canonical definition from docs/constraints.md.

3) THEME LEGEND (exact codes)
Define THEMES as an ordered dict/list of dicts keyed by code, each with: code, name, meaning, keywords (list[str]), control (bool), out_of_scope (bool), excluded_from_metric (bool).
Codes/names:
- T1_POST_SERVICE_CLOSURE — "After service, no clear next step/closure; need fades"
- T2_NEED_RECOGNITION — "Customer doesn't recognize when next need arises"
- T3_MENTAL_AVAILABILITY — "UC not top-of-mind when need arises"
- T4_CATEGORY_AWARENESS — "Customer unaware UC offers needed category"
- T5_LOCAL_WHATSAPP_DEFAULT — "Defaults to local provider/neighbour/WhatsApp/family"
- T6_DECISION_CONFIDENCE — "Unsure what service is needed / DIY vs professional"
- T7_PLANNING_SEASONALITY — "Need is seasonal/planned but not anticipated"
- T8_EXPERIENCE_QUALITY — "Service quality/experience issue" (control)
- T9_PRICE_OFFER — "Price/discount/incentive expectation" (control, out_of_scope=True)
- T10_REDO_REFUND — "Redo/warranty/refund case" (excluded_from_metric=True)
- T11_UNCLASSIFIED — "Insufficient signal"

Also define:
- BIAS_FLAGS = ["bad_experience_overrepresented", "silent_nonreturner_proxy", "none"]
- RETURN_SIGNALS = ["returned", "did_not_return", "unclear"]
- SOURCE_CLASSES = ["app_store","play_store","trustpilot","reddit","youtube","social","transcript","news","forum","other"]

4) SEGMENT
- SEGMENT_NAME = "Urban renters/families in metros who used one core category once and then went quiet"
- SEGMENT_NOTES = dict with keys: city_tier, household, categories_focus, behavior, excluded. Fill with sensible defaults; mark as hypothesis where needed.

5) DECOMPOSITION D1..D6
List of dicts with keys: id, stage, question, customer_can_answer, public_proxy, influenceable (bool), publicly_measurable (bool), notes.
Stages: D1 Need incidence, D2 Need recognition, D3 Mental availability, D4 Category consideration, D5 Choice vs alternatives, D6 Frictionless completion. Set influenceable/publicly_measurable thoughtfully; D1 mostly not influenceable.

6) PALETTE (colour-blind-safe; never red/green-only encoding)
PALETTE = {
  "ink": "#12212B",
  "teal": "#0B6E4F",
  "amber": "#E08A00",
  "blue": "#2C6EAA",
  "grey": "#6B7A83",
  "light": "#F3F6F5",
  "white": "#FFFFFF",
}

7) LIMITS / QA CONSTANTS
- GOLDEN_N = 20
- INTERVIEW_MIN = 5
- INTERVIEW_MAX = 6
- DECK_MAX_SLIDES = 10
- MIN_FONT_PT = 14
- MAX_PDF_MB = 40
- MIN_CORPUS = 150
- FELLOW_NAME_TO_EXCLUDE = ""  # set locally before final QA; do not commit personal name
- DECK_PDF_NAME = "NL_UrbanCompany.pdf"

8) GUARDRAILS
- FORBIDDEN_PATTERNS = [ ... ]  # lowercase patterns/regex fragments for QA scan: discount, coupon, promo, cashback, membership, free trial, voucher, referral bonus, price change, lower price, cheaper, professional pay, partner earnings, commission change, book now, book again, schedule now, pay now, checkout, message professional, contact pro, cancel booking, modify booking, bad experience (as root-cause framing), offer to come back
- ALLOWED_FRAMING_NOTE = "Focus on customer-side planning, awareness, decision confidence, timing, and continuity."

Show me the complete file after creating it.
```

## P3 — PII + ingestion with provenance

```text
Respect docs/constraints.md. Create src/pii.py and src/ingest.py.

pii.py (pure, no pandas): REDACTED="[REDACTED]"; redact_pii(text), redact_pii_counted(text)->(str,int), contains_pii(text)->bool. Replace emails, URLs, @handles, Indian phones (+91 / 10-digit with separators), UPI-like ids, standalone >=8-digit numbers. Collapse repeated [REDACTED]. __main__ demo with assertions.

ingest.py:
- load_corpus(path=None) reads data/public_corpus.csv with required columns: item_id, source, source_url, date, text. Optional: rating, city, category, hint_return_signal.
- Validate: every row has a non-empty source and source_url; if source_url domain contains "urbancompany.com" AND path looks logged-in/app/account, raise ValueError (C3).
- Redact text BEFORE anything else; drop items < 20 chars; dedupe by cleaned text; store df.attrs = {rows_loaded, redactions, sources_count, min_date, max_date}.
- paste_corpus(text_block, source, source_url) -> DataFrame so the Streamlit page can accept pasted public text.
- build_sample_corpus() writes a clearly-labelled ILLUSTRATIVE 40-row sample across sources (App Store, Play Store, Trustpilot, Reddit, YouTube comments, earnings transcript) with varied return signals — used only when data/public_corpus.csv is empty.
- assert no contains_pii remains.

Show both files and run `python -m src.pii` plus `python -c "import src.ingest as i; print(i.build_sample_corpus().shape)"`.
```

## P4 — Taxonomy + LLM coding engine

```text
Respect docs/constraints.md. Create src/taxonomy.py and src/engine.py.

taxonomy.py: THEME_DEFINITIONS with "include" and "exclude" guidance per theme (critical for T8 vs T1: a complaint about dirt left behind is EXPERIENCE; "I didn't think of anything else to book" is POST_SERVICE_CLOSURE). Add RETURN_SIGNAL_RULES and a few SAMPLING_NOTES about the two biases.

engine.py:
- code_item(text, llm) -> dict with keys: primary_theme, secondary_theme, return_signal, sentiment, bias_flag, confidence, rationale, quote_worthy, exact_quote.
  Call llm.generate_json(system, prompt) (add that helper to src/llm.py: strict JSON, strip code fences, retry once, return None on failure).
  System prompt must: define all 11 themes with include/exclude, demand one primary theme from the fixed list, forbid inventing themes, require a verbatim quote (<=140 chars) only when quote_worthy, and require a one-sentence rationale grounded in the text. temperature 0.0.
- code_corpus(df, llm, progress=None) -> themed DataFrame; deterministic fallback: keyword scorer using config.THEME_KEYWORDS + regex rules when llm returns None. Always fills every field.
- aggregate(df) -> dict: theme counts/shares, shares stratified by source and category, return_signal cross-tab, bias_flag counts, top verbatim quotes per theme (max 3), and a "continuity_vs_experience" split (T1-T7 vs T8/T9/T10).
- bias_report(df) -> dict: source mix, % from complaint-heavy sources, count of silent_nonreturner_proxy items, and an explicit limitation sentence about customers who leave no trace.
- run(corpus_path, llm) writes outputs/discovery_results.json.

Show files. Verify with the sample corpus and print the theme table.
```

## P5 — Golden set + evaluation + corrections

```text
Respect docs/constraints.md. Create src/eval.py.

- load_golden() reads data/golden_set.csv: item_id, text, human_primary_theme, human_return_signal, human_note. If it has < 20 rows, generate a TEMPLATE of exactly 20 rows from the sample corpus with human labels left blank and print instructions — never silently fabricate human labels.
- evaluate(themed_df, golden_df) -> dict: overall agreement %, per-theme precision/recall/support, confusion matrix (sklearn), return-signal agreement, list of disagreements with item_id, text, engine label, human label, human_note.
- corrections() returns 2-3 dicts in the exact shape {item_id, ai_output, human_correction, why_it_was_wrong, what_we_changed_in_the_prompt}. Seed these with placeholders I will fill from real disagreements.
- render_evidence_md(results, eval_result, corrections, sources) -> markdown string with sections: Sources & Volume table, Theme taxonomy, Golden set agreement + confusion matrix, Corrections, Bias handling, Limitations.
- export: write outputs/evidence_log.md and PDF via src.export.md_to_pdf().

Show the file. Print a sample evaluate() output using the template.
```

## P6 — Decomposition + opportunity scoring

```text
Respect docs/constraints.md. Create src/opportunity.py.

- decompose() returns the D1..D6 chain from config with, for each stage: a plain-language question a customer can answer, a public-data proxy, influencable Y/N, and why.
- score_opportunities(discovery, interviews_summary=None) -> ranked list. Score = reach (theme share, 0-5) x influenceability (customer-side, 0-5) x metric_link (which D stage and 90-day timing, 0-5) x evidence_strength (public + interview, 0-5). Include a "cannot influence" exclusion for T9 price/offer.
- map_to_metric(stage) -> text explaining how moving that stage changes the 90-day repeat share without creating false needs.
- Return a dataframe ready for an Altair chart.

Show file + print ranked opportunities on the sample results.
```

## P7 — MVP logic (the most important file)

```text
Respect docs/constraints.md. Create src/mvp.py.

Build a deterministic-first, LLM-enhanced "Home Care Companion". It must be usable with NO API key.

DATA:
- PROFILE_QUESTIONS: exactly 6, no PII: city_tier (metro/tier2), home_type (apartment/independent), household (family/kids/pets), categories_used_before (multi), months_since_last_service, planning_style (planned/reactive/avoided).
- PUBLIC_REFERENCE loaded from data/public_reference.csv (columns: need, trigger, typical_timing_days, public_basis, source_url) with ~15 public, non-UC-specific facts (monsoon humidity, pre-summer AC servicing, festival deep clean, pest season, water purifier filter cadence, etc.). Never claim these are UC facts.

FUNCTIONS:
- build_calendar(profile, reference, llm=None) -> list of {need, when_days, why, confidence, basis, source_url, route_hint}; rank by profile; cap at 6; every item must carry a public basis and source_url. If llm is None, pure rule scoring.
- route_need(text, profile, llm=None) -> dict {route, confidence, reason, clarifying_questions, used_public_reference, tool_trace}. Routes exactly: DIY, LOCAL_OR_NEIGHBOUR, UC_CATEGORY, WAIT_AND_WATCH, SEEK_IMMEDIATE_HELP. Rules:
   * urgent keywords (gas smell, bursting pipe, sparks, flooding) -> SEEK_IMMEDIATE_HELP, never a service recommendation.
   * simple DIY (cleaning a filter, tightening a tap, wiping AC vents) -> DIY with steps.
   * building/electrician/neighbour tasks -> LOCAL_OR_NEIGHBOUR.
   * vague input (< 12 words or no object) -> ask 2 clarifying questions, DO NOT recommend anything.
   * only when a need is clearly a core category AND confidence >= 0.6 -> UC_CATEGORY, and then show public UC category info text only (no booking link, no CTA that books).
   * Always produce a "why not the other routes" line.
- reflect(post_service_text) -> {open_topics: [...], unmet_expectation: bool, followup_question: str}
- log_tool_trace(record) appends {ts, session_hash, turn, chosen_tool, reason, user_input_length, route, confidence} to outputs/tool_trace.jsonl. Tools named: ask_clarifying_question, public_reference_lookup, build_calendar, route_need, capture_reflection, show_public_info.
- log_feedback(record) appends to outputs/mvp_feedback.jsonl.

HARD GUARDS:
- No requests/httpx/urllib calls anywhere. No strings containing "book now", "book again", "coupon", "discount", "offer", "pay", "checkout".
- A module-level assert on import: inspect source of this file and raise if forbidden strings or network imports appear.

Show the file and run a quick CLI demo of three needs: "AC not cooling", "tap dripping", "something feels off in my kitchen but not sure what".
```

## P8 — Streamlit shell + navigation + shared CSS

```text
Respect docs/constraints.md. Create app.py as the router AND the MVP page.

At startup mirror st.secrets into os.environ for GEMINI_API_KEY / GEMINI_MODEL (same pattern as my Groww app.py).
st.set_page_config(title="Urban Company — Home Care Companion", icon="🏠", layout="wide").
Add accessible CSS: ink on white, focus outlines, min font 14px for body, tabs with text labels not colour-only.
Build navigation with st.navigation([...]) using st.page("views/1_MVP.py", ...) etc. Put the MVP FIRST with default=True so root URL opens it. views/1_MVP.py should just import and call a render() from a shared module OR keep the MVP UI in app.py and make views/1_MVP.py a thin re-export — your choice, but avoid duplicate UI code.
Add a persistent sidebar footer: "Public prototype · No bookings · No account access · Public information only".

Show app.py.
```

## P9 — Discovery Engine page + Evidence Log page

```text
Respect docs/constraints.md. Create views/2_Discovery_Engine.py and views/3_Evidence_Log.py.

Discovery Engine page:
- Sidebar: source filter, theme filter, "Use bundled sample" toggle, "Run engine" button, LLM status banner (live/offline).
- Main: st.file_uploader for public corpus CSV; st.text_area for pasted public text with source + URL fields.
- On run: ingest -> engine.code_corpus -> engine.aggregate -> engine.bias_report; show KPI row (items, sources, themes, continuity-vs-experience split, agreement-if-golden-present); Altair bar of theme shares; stacked bar share by source; table of top quotes; bias callout with explicit limitation text.
- A one-slide "How it works" block (5 numbered steps + inputs/outputs diagram) — this exact block will be reused in the deck.
- st.download_button for outputs/discovery_results.json.

Evidence Log page:
- Render sections from src.eval.render_evidence_md: Sources & Volume table (from df.attrs), golden set agreement (big number), per-theme precision/recall table, confusion matrix heatmap, corrections cards, bias handling, limitations.
- File uploader to load the golden set; button to (re)compute agreement against current results.
- Download buttons: evidence_log.md and evidence_log.pdf.
- Banner: "Anyone with the link can view — no login".

Show both files.
```

## P10 — MVP UI (main testable experience)

```text
Respect docs/constraints.md. Create views/1_MVP.py (or app.py MVP renderer per P8).

A 4-step wizard with st.progress and clear step labels:
Step 1 "Tell me about your home" -> 6 profile questions from mvp.PROFILE_QUESTIONS. No name, phone, address, flat number, or booking screenshots. Show a visible "We don't ask for personal details" note.
Step 2 "Your next 90 days" -> build_calendar, show cards with need / when / why / public basis / source link. Label confidence. Add an editable "add a need I'm already thinking about" text box.
Step 3 "Need Decider" -> chat-like text input. On submit: route_need, display route + reason + "why not the other routes" + clarifying questions when vague. Log every turn with log_tool_trace. Show a small transparent "Tool used this turn: ..." chip (needed for Part 7 tool-choice measurement).
Step 4 "After a service" -> reflect(), capture open topics as a private, downloadable personal checklist (no upload), and a 2-question feedback widget (was this useful / did this match a real need) -> log_feedback.
End screen: "Nothing here books anything. These are public facts and your own notes."

Add a "Demo tasks for mentors" expander with 3 real tasks to try.
Persist all state in st.session_state. Handle offline mode gracefully.

Show the file.
```

## P11 — Research, problem, testing, success, risks pages

```text
Respect docs/constraints.md. Create views/4_Metric_Decomposition.py, views/5_User_Research.py, views/6_Problem_Definition.py, views/7_MVP_Testing.py, views/8_Success_Metrics.py, views/9_Risks.py.

Use src/research.py helpers (create it): load_interviews() validates columns respondent_id (R01..R06), category, returner_90d (yes/no), total_bookings (int), city_tier, and coded quote fields; NO columns for name/phone/address/screenshot; raise if any PII-like column exists.

4_Metric: draw D1..D6 as a numbered flow with influencable/not badges, exact metric definition box, and "how we'd measure with only customer self-report or public data".
5_User_Research: interview protocol (questions from the brief), respondent table with booking counts, anonymity note, and a synthesis of validates/challenges vs AI findings. Include empty-state placeholders I will fill with my 5-6 interviews.
6_Problem_Definition: a 6-arrow evolution chain Business Metric -> Product Outcomes -> AI Discovery -> Primary Research -> Problem Definition, then the structured problem statement (segment, scenario, product outcome, root cause, workarounds, user value, business sense) with explicit "not a bad experience, not an offer" callout.
7_MVP_Testing: 3-return-user test plan with task, expected tool trace, observed, change for next iteration (placeholder cards).
8_Success_Metrics: business metric -> leading indicators -> guardrails table with definitions, rationale, target, and measurement source. Include the tool-choice section: 10 golden tasks with expected tool traces, precision/recall of tool choice, and 3 anti-nudge guardrails (non-UC route rate, no-need rate, 2-week "did I actually need it" follow-up).
9_Risks: 6 risks x likelihood x impact x mitigation x early-warning signal (colour + label).

Show all files.
```

## P12 — Deck page + PDF export

```text
Respect docs/constraints.md. Create src/deck.py and views/10_Deck.py.

src/deck.py: SLIDES = list of 10 dicts with {n, title, key_message, bullets, visual, footnote_links, source_refs}. Titles MUST be full sentences stating the key message (no "Problem", "Solution"). Slide titles exactly:
1. "One in three repeat bookings is decided in the 90 days after the first service, not during it" (title slide also includes "Urban Company · Consumer Growth · Nov 2026" and NO fellow name)
2. "The 90-day repeat rate is six customer decisions, only four of which the product can influence"
3. "Our discovery engine codes public conversations into 11 opportunity themes and corrects for two known biases" (the required 1-slide engine explanation)
4. "Continuity signals outweigh service-quality complaints in the public corpus"
5. "Six interviews split evenly between returners and non-returners show the same pattern in customers' own words"
6. "We chose metro households who used one core category once and then went quiet"
7. "The root cause is a missing handoff from 'job done' to 'what's next for my home'"
8. "A Home Care Companion builds the next need before it becomes urgent, and honestly says when not to book"
9. "Three return users completed real tasks; two friction points changed the next iteration"
10. "Success is a higher 90-day repeat rate with no increase in unnecessary bookings"
Add slides for success metrics and risks inside slides 9/10 as compact panels so we stay at 10.

build_pdf() uses reportlab platypus: A4 landscape, base font 14pt minimum (titles 22pt), body 14pt, table 12pt ONLY if unavoidable — otherwise 14pt, palette from config, no red/green-only encoding, footer with page number, output outputs/deck.pdf. QA: assert filename "NL_UrbanCompany.pdf", pages <=10, estimated size <40MB, and scan all text for the fellow's name (ask me for the name to exclude via a constant FELLOW_NAME_TO_EXCLUDE = "" in config so we can assert it is absent without printing it).

views/10_Deck.py: render slides as styled st.container cards with message-first titles, Altair mini-charts where specified, hyperlinked supporting artefacts, and a st.download_button for the PDF. Add a spacing/font QA badge.

Show files and run build_pdf(); report page count and file size.
```

## P13 — QA, README, deploy doc

```text
Respect docs/constraints.md. Create scripts/qa_check.py, docs/qa_report.md, README.md, docs/deploy_streamlit_cloud.md, docs/sources.md, docs/methodology.md, docs/demo_script.md.

qa_check.py must assert and print PASS/FAIL:
- no forbidden phrases (C1) in src/mvp.py, views/1_MVP.py, outputs/deck.pdf text
- no requests/httpx/urllib/socket in src/mvp.py or any views/ (C2, C3)
- "urbancompany.com" only appears in docs/ and provenance URLs, never as a booking target
- golden set has 20 labelled rows (prompt me if blank, do not fabricate)
- interviews has 5-6 rows, both returner values present, >=2 categories, total_bookings filled
- deck page count <=10, no fellow name, min font >=14
- evidence log downloads exist and are non-empty

README: architecture diagram, how to run locally, how to run the pipeline, how to re-collect data, links placeholder for deployed URLs, and the exact submission checklist.
deploy doc: adapt my Groww deploy doc to this app — GitHub push, share.streamlit.io, main file app.py, requirements-cloud.txt, secrets block with GEMINI_API_KEY, Wake up note, and the reminder that free tier has ephemeral disk so use download buttons for deliverables.
sources.md: table of source class, what we took, URL pattern, public access confirmation, and what we did NOT access.

Show all files and run `python -m scripts.qa_check`.
```
