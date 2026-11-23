"""AI Discovery Engine page. Respect docs/constraints.md (C3, C10)."""

from __future__ import annotations

import json

import altair as alt
import pandas as pd
import streamlit as st

from src import config, engine, eval as eval_mod, ingest, llm


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