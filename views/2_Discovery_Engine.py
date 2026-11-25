"""AI Discovery Engine page. Respect docs/constraints.md (C3, C10)."""

from __future__ import annotations

import json

import altair as alt
import pandas as pd
import streamlit as st

from src import config, discovery_questions, engine, eval as eval_mod, ingest, llm, opportunity


def _load_default_corpus(use_sample: bool = False):
    """Load the real public corpus by default; the illustrative sample is opt-in.

    Returns (dataframe, source path, sample_used).
    """
    config.ensure_dirs()
    sample = config.DATA_DIR / "public_corpus_sample.csv"
    if use_sample:
        if not sample.exists():
            ingest.build_sample_corpus(sample, write=True)
        return ingest.load_corpus(sample), sample, True
    if config.CORPUS.exists():
        return ingest.load_corpus(config.CORPUS), config.CORPUS, False
    if not sample.exists():
        ingest.build_sample_corpus(sample, write=True)
    return ingest.load_corpus(sample), sample, True


def render() -> None:
    st.title("AI Discovery Engine")
    st.caption("Public-source feedback coding into fixed opportunity themes. No logged-in UC scraping.")
    with st.expander("Eligible public sources and current coverage"):
        st.markdown(
            """
            Eligible: Apple App Store, Google Play, Trustpilot/consumer forums, Reddit (Indian city/household communities),
            public social conversations, YouTube comments, UC public shareholder letters, public earnings-call transcripts,
            and other public home-service conversations. No logged-in or private UC surfaces.
            """
        )
        st.caption("Current corpus: App Store (India) only — single-source and complaint-heavy. See docs/sources.md.")

    with st.sidebar:
        st.subheader("Discovery controls")
        use_sample = st.toggle("Use bundled illustrative sample", value=False)
        run_btn = st.button("Run engine", type="primary", width="stretch")
        st.divider()
        st.write("LLM status")
        if llm.available():
            st.success(f"Live LLM: {llm.active_model()}")
        else:
            st.info("Offline deterministic fallback (no GEMINI_API_KEY).")

    uploaded = st.file_uploader("Upload public corpus CSV", type=["csv"])
    with st.expander("Paste public text (optional)"):
        paste_source = st.text_input("Source name", value="Pasted public source")
        paste_class = st.selectbox("Source class", config.SOURCE_CLASSES, index=0)
        paste_url = st.text_input("Source URL (public)", value="https://example.com/public-source")
        paste_text = st.text_area("One item per line", height=120)

    if "discovery_results" not in st.session_state:
        st.session_state.discovery_results = None
        st.session_state.discovery_df = None

    if run_btn:
        try:
            if uploaded is not None and not use_sample:
                tmp = config.OUTPUTS_DIR / "_uploaded_corpus.csv"
                tmp.write_bytes(uploaded.getbuffer())
                df = ingest.load_corpus(tmp)
                src_path = tmp
                sample_used = False
            else:
                df, src_path, sample_used = _load_default_corpus(use_sample)

            if paste_text.strip():
                pasted = ingest.paste_corpus(paste_text, paste_source, paste_url, paste_class)
                if not pasted.empty:
                    df = pd.concat([df, pasted], ignore_index=True).drop_duplicates(subset=["text"])

            coded = engine.code_corpus(df, llm=llm)
            results = {
                "generated_at": pd.Timestamp.utcnow().isoformat(),
                "corpus": {
                    "rows_loaded": df.attrs.get("rows_loaded", len(df)),
                    "rows_kept": len(df),
                    "redactions": df.attrs.get("redactions", 0),
                    "sources_count": df.attrs.get("sources_count", int(df["source"].nunique()) if "source" in df.columns else 0),
                    "min_date": df.attrs.get("min_date"),
                    "max_date": df.attrs.get("max_date"),
                    "illustrative": bool(df["is_illustrative"].any()) if "is_illustrative" in df.columns else False,
                    "source_file": str(src_path),
                },
                "aggregate": engine.aggregate(coded),
                "bias_report": engine.bias_report(coded),
                "items": coded.to_dict(orient="records"),
            }
            # Demo runs on the illustrative sample must never overwrite the
            # canonical evidence outputs produced from the real public corpus.
            out_path = (
                config.OUTPUTS_DIR / "discovery_results_sample.json"
                if sample_used
                else config.DISCOVERY_JSON
            )
            out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
            st.session_state.discovery_results = results
            st.session_state.discovery_df = coded
            if sample_used:
                st.warning("Illustrative sample results saved separately; canonical evidence outputs unchanged.")
            st.success(f"Discovery engine run complete — saved to {out_path.name}.")
        except Exception as e:
            st.error(f"Run failed: {e}")

    results = st.session_state.discovery_results
    coded = st.session_state.discovery_df
    if not results:
        st.info("Run the engine to generate coded themes, bias report, and evidence outputs.")
        return

    corpus = results.get("corpus", {})
    agg = results.get("aggregate", {})
    bias = results.get("bias_report", {})
    if corpus.get("illustrative"):
        st.warning("Illustrative sample in use. Replace with real public evidence before submission.")

    # Golden agreement if available
    golden = eval_mod.load_golden()
    eval_result = eval_mod.evaluate(coded, golden) if coded is not None else {"status": "incomplete", "agreement_pct": None}

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Items", agg.get("total_items", 0))
    k2.metric("Sources", corpus.get("sources_count", 0))
    k3.metric("Themes present", sum(1 for r in agg.get("theme_distribution", []) if r.get("count", 0) > 0))
    cve = agg.get("continuity_vs_experience", {})
    k4.metric("Continuity %", f"{cve.get('continuity_pct', 0)}%")
    k5.metric("Golden agreement", f"{eval_result.get('agreement_pct', 'N/A')}%")

    st.subheader("Theme distribution")
    dist_df = pd.DataFrame(agg.get("theme_distribution", []))
    if not dist_df.empty:
        chart = alt.Chart(dist_df).mark_bar().encode(
            x=alt.X("share_pct:Q", title="Share (%)"),
            y=alt.Y("code:N", sort="-x", title="Theme"),
            color=alt.Color("code:N", legend=None),
            tooltip=["code", "name", "count", "share_pct"],
        ).properties(height=320)
        st.altair_chart(chart, width="stretch")

    st.subheader("Share by source class")
    src_df = pd.DataFrame(agg.get("by_source_class", []))
    if not src_df.empty:
        chart2 = alt.Chart(src_df).mark_bar().encode(
            x=alt.X("count:Q", title="Items"),
            y=alt.Y("source_class:N", title="Source class"),
            color=alt.Color("primary_theme:N", title="Theme"),
            tooltip=["source_class", "primary_theme", "count"],
        ).properties(height=260)
        st.altair_chart(chart2, width="stretch")

    st.subheader("Top quotes by theme")
    quotes = agg.get("top_quotes_by_theme", {})
    quote_rows = []
    for code, qlist in quotes.items():
        for q in qlist:
            quote_rows.append({"theme": code, **q})
    if quote_rows:
        st.dataframe(pd.DataFrame(quote_rows), width="stretch", hide_index=True)
    else:
        st.info("No quotes available yet.")

    st.subheader("Bias report")
    st.warning(bias.get("limitation", "Bias limitation unavailable."))
    st.json({k: v for k, v in bias.items() if k != "limitation"})

    st.subheader("Part 1 discovery questions — evidence status")
    st.dataframe(discovery_questions.question_report_dataframe(results), width="stretch", hide_index=True)
    for q in discovery_questions.build_question_report(results):
        with st.expander(f"{q['id']} · {q['question']}"):
            st.write("**Status:**", q["status"])
            st.write("**Detail:**", q["detail"] or "—")
            st.caption(q["note"])
            for ex in q["example_quotes"]:
                st.markdown(f"> “{ex['quote']}” — {ex['item_id']} ({ex['source']})")
            if not q["example_quotes"]:
                st.info("No verbatim evidence for this question in the current corpus.")

    st.subheader("Segmentation coverage")
    st.json(agg.get("segmentation_coverage", {}))
    st.caption("Empty fields are reported as zero coverage — never treated as evidence.")

    st.subheader("Opportunity ranking")
    opp = opportunity.opportunities_dataframe(results)
    if not opp.empty:
        cols = ["rank", "theme_code", "share_pct", "stage", "reach_0_5", "influenceability_0_5",
                "metric_link_0_5", "evidence_strength_0_5", "score", "status"]
        st.dataframe(opp[cols], width="stretch", hide_index=True)
        eligible = opp[~opp["excluded"]]
        if not eligible.empty:
            chart_opp = alt.Chart(eligible).mark_bar().encode(
                x=alt.X("score:Q", title="Heuristic score"),
                y=alt.Y("label:N", sort="-x", title="Theme"),
                tooltip=["theme_code", "share_pct", "score", "stage"],
            ).properties(height=300)
            st.altair_chart(chart_opp, width="stretch")
        st.caption("Weights are hand-set heuristics, not data-derived; price themes are excluded under C1. Not validated until interviews are complete.")

    st.subheader("How it works (1-slide block)")
    st.markdown(
        """
        1. **Ingest public sources** — load public CSV or pasted public text; log source URL/class/date; block logged-in UC/app paths.  
        2. **Redact & clean** — remove PII, dedupe, keep provenance.  
        3. **Code with fixed taxonomy** — assign T1–T11, return signal, bias flag; LLM when available, deterministic fallback otherwise.  
        4. **Aggregate & score** — theme shares, continuity vs experience split, bias report, opportunity ranking.  
        5. **Validate & publish** — golden-set agreement, human corrections, evidence log, and Streamlit deliverable.  

        **Inputs:** public reviews/posts/transcripts. **Outputs:** coded items, theme table, bias report, evidence log.
        """
    )

    st.download_button(
        "Download discovery_results.json",
        data=json.dumps(results, indent=2, ensure_ascii=False).encode("utf-8"),
        file_name="discovery_results.json",
        mime="application/json",
    )


render()