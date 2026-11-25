"""AI Evidence Log page. Respect docs/constraints.md (C10)."""

from __future__ import annotations

import json
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from src import config, engine, eval as eval_mod, ingest
from src.export import md_to_pdf_bytes


def render() -> None:
    st.title("AI Evidence Log")
    st.success("Anyone with the link can view — no login.")
    st.caption("Public evidence log: sources, golden-set evaluation, corrections, and bias handling.")

    config.ensure_dirs()
    sample_path = config.DATA_DIR / "public_corpus_sample.csv"
    if not sample_path.exists():
        ingest.build_sample_corpus(sample_path, write=True)

    if config.DISCOVERY_JSON.exists():
        results = json.loads(config.DISCOVERY_JSON.read_text(encoding="utf-8"))
    else:
        results = engine.run(sample_path, llm=None, out_path=config.OUTPUTS_DIR / "discovery_results_sample.json")

    coded = pd.DataFrame(results.get("items", []))
    golden = eval_mod.load_golden()

    st.subheader("Golden set")
    uploaded = st.file_uploader("Upload golden_set.csv (optional)", type=["csv"], key="golden_upload")
    if uploaded is not None:
        gdf = pd.read_csv(uploaded)
        gdf.to_csv(config.GOLDEN, index=False)
        golden = eval_mod.load_golden()
        st.success("Golden set uploaded.")

    st.subheader("Label the golden set here")
    st.caption("20 rows. Choose a fixed theme and return signal for every row, then save. Nothing is auto-labelled.")
    editor = st.data_editor(
        golden,
        key="golden_editor",
        width="stretch",
        hide_index=True,
        column_config={
            "item_id": st.column_config.TextColumn("item_id", disabled=True),
            "text": st.column_config.TextColumn("text", disabled=True, width="large"),
            "human_primary_theme": st.column_config.SelectboxColumn(
                "human_primary_theme", options=["TODO"] + [str(c) for c in config.THEME_CODES]
            ),
            "human_return_signal": st.column_config.SelectboxColumn(
                "human_return_signal", options=["TODO"] + [str(s) for s in config.RETURN_SIGNALS]
            ),
            "human_note": st.column_config.TextColumn("human_note"),
        },
    )
    if st.button("Save golden labels"):
        bad = editor[
            (~editor["human_primary_theme"].isin(set(config.THEME_CODES)))
            | (~editor["human_return_signal"].isin(set(config.RETURN_SIGNALS)))
        ]
        if len(editor) != config.GOLDEN_N or not bad.empty:
            st.error(f"Need all {config.GOLDEN_N} rows labelled with valid codes; {len(bad)} rows are still invalid.")
        else:
            editor.to_csv(config.GOLDEN, index=False)
            st.session_state.pop("eval_result", None)
            st.success("Golden labels saved. Agreement metrics are now computed from real human labels.")
            st.rerun()

    if st.button("Recompute agreement"):
        if not config.DISCOVERY_JSON.exists():
            engine.run(sample_path, llm=None, out_path=config.OUTPUTS_DIR / "discovery_results_sample.json")
        coded = pd.DataFrame(results.get("items", []))
        golden = eval_mod.load_golden()
        st.session_state["eval_result"] = eval_mod.evaluate(coded, golden)

    eval_result = st.session_state.get("eval_result") or eval_mod.evaluate(coded, golden)
    corr = eval_mod.corrections()

    c1, c2, c3 = st.columns(3)
    c1.metric("Labelled rows", f"{eval_result.get('n_labelled', 0)}/{eval_result.get('n_required', config.GOLDEN_N)}")
    c2.metric("Agreement", f"{eval_result.get('agreement_pct', 'N/A')}%")
    c3.metric("Return-signal agreement", f"{eval_result.get('return_signal_agreement_pct', 'N/A')}%")
    st.info(eval_result.get("message", "Evaluation computed from available golden labels."))

    st.subheader("Sources & volume")
    corpus = results.get("corpus", {})
    by_src = {}
    for it in results.get("items", []):
        by_src[str(it.get("source", "unknown"))] = by_src.get(str(it.get("source", "unknown")), 0) + 1
    src_df = pd.DataFrame([{"source": k, "count": v} for k, v in sorted(by_src.items())])
    st.dataframe(src_df, width="stretch", hide_index=True)
    st.write({
        "rows_loaded": corpus.get("rows_loaded"),
        "rows_kept": corpus.get("rows_kept"),
        "redactions": corpus.get("redactions"),
        "illustrative": corpus.get("illustrative"),
    })

    st.subheader("Per-theme precision/recall")
    per_theme = eval_result.get("per_theme", {})
    if per_theme:
        pt_df = pd.DataFrame([
            {"theme": k, "precision": v.get("precision"), "recall": v.get("recall"), "f1": v.get("f1-score"), "support": v.get("support")}
            for k, v in per_theme.items()
        ])
        st.dataframe(pt_df, width="stretch", hide_index=True)
    else:
        st.warning("Per-theme metrics will appear after golden set is fully labelled.")

    st.subheader("Confusion matrix")
    cm = eval_result.get("confusion_matrix", [])
    labels = eval_result.get("labels", [])
    if cm and labels:
        cm_rows = []
        for i, row in enumerate(cm):
            for j, val in enumerate(row):
                cm_rows.append({"human": labels[i], "engine": labels[j], "count": val})
        cm_df = pd.DataFrame(cm_rows)
        heat = alt.Chart(cm_df).mark_rect().encode(
            x=alt.X("engine:N", title="Engine"),
            y=alt.Y("human:N", title="Human"),
            color=alt.Color("count:Q", scale=alt.Scale(scheme="blues")),
            tooltip=["human", "engine", "count"],
        ).properties(height=360)
        text = heat.mark_text(baseline="middle").encode(text="count:Q", color=alt.value("#12212B"))
        st.altair_chart(heat + text, width="stretch")
    else:
        st.warning("Confusion matrix will appear after golden set is fully labelled.")

    st.subheader("Corrections")
    for c in corr:
        with st.container(border=True):
            st.markdown(f"**{c.get('item_id')}**")
            st.write("AI output:", c.get("ai_output"))
            st.write("Human correction:", c.get("human_correction"))
            st.write("Why it was wrong:", c.get("why_it_was_wrong"))
            st.write("What changed:", c.get("what_we_changed_in_the_prompt"))

    st.subheader("Bias handling")
    bias = results.get("bias_report", {})
    st.write(bias)
    st.warning(bias.get("limitation", ""))

    cov_path = config.OUTPUTS_DIR / "source_availability.json"
    if cov_path.exists():
        st.subheader("Public source availability")
        cov = json.loads(cov_path.read_text(encoding="utf-8"))
        cov_df = pd.DataFrame(cov.get("rows", []))
        if not cov_df.empty:
            st.dataframe(
                cov_df[["source", "source_class", "http_status", "reachable", "error"]],
                width="stretch", hide_index=True,
            )
        st.caption("Availability probe only. Unreachable sources contributed no data; nothing was invented.")

    audit_path = config.OUTPUTS_DIR / "audit_results.json"
    if audit_path.exists():
        st.subheader("AI tool-choice audit (system self-check)")
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
        a1, a2, a3, a4 = st.columns(4)
        a1.metric("Tool accuracy", f"{audit.get('tool_accuracy_pct')}%")
        a2.metric("Route accuracy", f"{audit.get('route_accuracy_pct')}%")
        a3.metric("No-action routes", f"{audit.get('no_action_route_pct')}%")
        a4.metric("Incorrect routes", f"{audit.get('incorrect_route_pct')}%")
        st.dataframe(pd.DataFrame(audit.get("rows", [])), width="stretch", hide_index=True)
        st.caption(audit.get("limitation", ""))

    st.subheader("Limitations")
    st.markdown(
        """
        - Public data over-represents vocal and negative experiences; quiet non-returners are under-observed.
        - Illustrative sample data, if used, is for workflow demonstration only and must be replaced before submission.
        - LLM coding is probabilistic; golden-set review and human corrections are required.
        - No PII, screenshots, invoices, addresses, phone numbers, or personal documents are included.
        """
    )

    md = eval_mod.render_evidence_md(results, eval_result, corr)
    st.download_button(
        "Download evidence_log.md",
        data=md.encode("utf-8"),
        file_name="evidence_log.md",
        mime="text/markdown",
    )
    try:
        pdf_bytes = md_to_pdf_bytes(md)
        st.download_button(
            "Download evidence_log.pdf",
            data=pdf_bytes,
            file_name="evidence_log.pdf",
            mime="application/pdf",
        )
    except Exception as e:
        st.info(f"PDF export unavailable in this environment: {e}. MD download is available.")


render()