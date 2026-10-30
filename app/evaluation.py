import altair as alt
import pandas as pd
import streamlit as st


# Fixed results copied from the referenced evaluation logs.
RETRIEVAL_LOG_FILENAME = "EVALUATE_RETRIEVAL_GPT_120B.txt"
RETRIEVAL_TEST_COUNT = 20
# Retrieval metrics are percentages, ready for display.
RETRIEVAL_RESULTS = {
    "k": [1, 3, 5, 10],
    "Hit@k": [85, 100, 100, 100],
    "Recall@k": [80, 95, 100, 100],
    "Precision@k": [85, 77, 60, 42],
}
EVALUATION_RUNS = (
    {
        "version": "v1",
        "change": "Baseline",
        "model": "Qwen 27B",
        "filename": "EVALUATE_CLASSIFIER_QWEN_27B_STRICT_FALSE_v1.txt",
        "passed": 201,
        "failed": 68,
    },
    {
        "version": "v2",
        "change": "Model change",
        "model": "GPT-OSS 120B",
        "filename": "EVALUATE_CLASSIFIER_GPT_120B_STRICT_TRUE_v2.txt",
        "passed": 223,
        "failed": 46,
    },
    {
        "version": "v3",
        "change": "Prompt adjustments",
        "model": "GPT-OSS 120B",
        "filename": "EVALUATE_CLASSIFIER_GPT_120B_STRICT_TRUE_v3.txt",
        "passed": 241,
        "failed": 28,
    },
)


def render_source_logs(sources):
    with st.expander("Source logs"):
        for label, filename in sources:
            st.caption(f"{label}: {filename}")


def render_classification_results():
    data = pd.DataFrame(EVALUATION_RUNS)
    data["accuracy"] = data["passed"] / (data["passed"] + data["failed"])
    data["accuracy_label"] = data["accuracy"].map("{:.2%}".format)
    results = data.to_dict("records")

    st.subheader("Classification accuracy")
    st.write("Tests how reliable the classifier was in cateogrizing a test dataset.")
    base = alt.Chart(data).encode(
        x=alt.X("version:O", title="Version", sort=["v1", "v2", "v3"], axis=alt.Axis(labelAngle=0)),
        y=alt.Y("accuracy:Q", title="Accuracy", scale=alt.Scale(domain=[0, 1]), axis=alt.Axis(format=".0%")),
        tooltip=[
            alt.Tooltip("version:O", title="Version"),
            alt.Tooltip("change:N", title="Change"),
            alt.Tooltip("model:N", title="Model"),
            alt.Tooltip("accuracy:Q", title="Accuracy", format=".2%"),
            alt.Tooltip("passed:Q", title="Correct", format="d"),
            alt.Tooltip("failed:Q", title="Incorrect", format="d"),
        ],
    )
    line = base.mark_line(color="#a78bfa", strokeWidth=3, point=alt.OverlayMarkDef(size=100))
    # A dark outline keeps the light labels readable in both light and dark themes.
    label_outline = base.mark_text(
        dy=-18, fontSize=14, stroke="#0f172a", strokeWidth=3, strokeJoin="round"
    ).encode(text="accuracy_label:N")
    labels = base.mark_text(dy=-18, fontSize=14, color="#f8fafc").encode(text="accuracy_label:N")
    st.altair_chart((line + label_outline + labels).properties(height=340), width="stretch")
    st.caption("Accuracy = correct category predictions / evaluated tickets.")
    for index, (column, result) in enumerate(zip(st.columns(3), results)):
        delta = None
        if index:
            improvement = (result["accuracy"] - results[index - 1]["accuracy"]) * 100
            delta = f"{improvement:+.2f}"
        column.metric(
            f"{result['version']} · {result['change']}",
            result["accuracy_label"],
            delta=delta,
        )

    render_source_logs([(result["version"], result["filename"]) for result in results])


def render_retrieval_results():
    st.subheader("Retrieval evaluation")
    st.write("How reliably the policy search retrieves relevant source material for a support question.")
    st.caption(
        f"{RETRIEVAL_TEST_COUNT} test questions · k is the number of policy chunks retrieved. "
        "Scores are averaged across the test questions."
    )
    percentages = pd.DataFrame(RETRIEVAL_RESULTS)
    st.dataframe(
        percentages,
        hide_index=True,
        width="stretch",
        column_config={
            "k": st.column_config.NumberColumn("Top k chunks", format="%d"),
            **{
                metric: st.column_config.NumberColumn(metric, format="%.0f%%")
                for metric in ("Hit@k", "Recall@k", "Precision@k")
            },
        },
    )
    with st.container(border=True):
        st.markdown(
            "- **Hit@k — Did we find anything useful?** How often the first k results "
            "include at least one expected policy file.\n\n"
            "- **Recall@k — How much of what we needed did we find?** The share of "
            "expected policy files found in the first k results.\n\n"
            "- **Precision@k — How much of what we found was useful?** The share of "
            "the first k chunks that come from expected policy files."
        )
    render_source_logs([("Retrieval", RETRIEVAL_LOG_FILENAME)])


def render():
    st.markdown('<div class="desk-label">SUPPORT DESK</div>', unsafe_allow_html=True)
    st.title("Evaluation")
    st.write("A summary of some of the evaluations carried out")
    st.info("For full evaluation details, refer to the source logs.")
    render_classification_results()
    st.divider()
    render_retrieval_results()
