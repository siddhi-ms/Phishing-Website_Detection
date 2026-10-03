"""Page 4 - Analytics (charts created by src/train.py + feature importance)."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import streamlit as st

from src.predict import MODEL_PATH
from src.preprocess import ASSETS_DIR
from utils import data
from utils.styles import card, grid, md, page_header, section, stat_card


def show_image(title, filename):
    st.markdown(f"**{title}**")
    path = ASSETS_DIR / filename
    if path.exists():
        st.image(str(path))
    else:
        st.info(f"{filename} not found. Run `python src/train.py`.")


def importance_chart():
    st.markdown("**Feature importance**")
    if not (data.model_ready() and data.dataset_stats()):
        st.info("Needs the trained model and dataset/phishing.csv.")
        return
    with st.spinner("Computing permutation importance on the test split..."):
        try:
            df = data.feature_importance(MODEL_PATH.stat().st_mtime).sort_values("importance")
        except Exception as exc:
            st.error(f"Could not compute feature importance: {exc}")
            return
    fig, ax = plt.subplots(figsize=(6, 4.2))
    fig.patch.set_facecolor("#111C31")
    ax.set_facecolor("#111C31")
    ax.barh(df["feature"], df["importance"] * 100, color="#3B82F6")
    ax.set_xlabel("Accuracy drop when shuffled (%)", color="#C9D6EA")
    ax.tick_params(colors="#C9D6EA", labelsize=8)
    for spine in ax.spines.values():
        spine.set_color("#1F2D4A")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    st.caption("Permutation importance of the trained ANN on the 20% test data: a bigger drop means the model relies more on that feature.")


def render():
    page_header("Analytics", "Dataset insights and model performance from the trained ANN.")
    metrics = data.load_metrics()
    if metrics:
        md(grid([
            stat_card("", "Accuracy", f"{metrics['accuracy'] * 100:.2f}%", "", "green"),
            stat_card("", "Precision", f"{metrics['precision'] * 100:.2f}%", "", "blue"),
            stat_card("", "Recall", f"{metrics['recall'] * 100:.2f}%", "", "purple"),
            stat_card("", "F1-score", f"{metrics['f1_score'] * 100:.2f}%", "", "amber"),
        ]))
    else:
        md(card("Metrics not available", "Run <span class='pg-code'>python src/train.py</span> to generate metrics and charts.", "", "amber"))

    section("Dataset and model visuals")
    c1, c2 = st.columns(2)
    with c1:
        show_image("Class distribution", "class_distribution.png")
    with c2:
        show_image("Confusion matrix", "confusion_matrix.png")
    c3, c4 = st.columns(2)
    with c3:
        show_image("Correlation heatmap", "correlation_heatmap.png")
    with c4:
        importance_chart()

    with st.expander("More charts"):
        show_image("Feature distributions", "feature_distributions.png")
        show_image("Training curves", "training_curves.png")
