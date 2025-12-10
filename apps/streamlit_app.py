import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
from pathlib import Path
import os 
import glob
import sys

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent
MODEL_PATH = PROJECT_ROOT.parent / 'models' / 'line_clf.joblib'
RAW_DATA_DIR = PROJECT_ROOT / 'data_raw'
PROCESSED_DIR = PROJECT_ROOT / 'data_processed'
TO_REVIEW_PATH = PROJECT_ROOT / "data_labels" / "to_review.csv"
DB_PATH = PROCESSED_DIR / 'workouts.db'
sys.path.append(str(Path(__file__).parent.parent.resolve()))
# Imports Parsers
from src.parsers.v1_parser import parse_log_content
from src.parsers.normalize import normalize_exercise
from src.parsers.hybrid_parse_all import ml_label_fn, save_review_fn
from src.parsers.feature_engineering import calculate_epley_1rm, run_feature_engineering

# Cache model loading
@st.cache_resource
def load_ml_model():
    if not MODEL_PATH.exists():
        st.error(f"ML model not found at {MODEL_PATH}.")
        return None
    return joblib.load(MODEL_PATH)

# Cache parsing 
@st.cache_data
def parse_file_content(text, source_file='Streamlit_upload', conf_threshold=0.60):
    rows = parse_log_content(
        text, 
        source_file=source_file,
        ml_label_fn=ml_label_fn,
        save_review_fn=save_review_fn,
        conf_threshold=conf_threshold
    )
    # Normalize exersises
    for r in rows:
        if 'exercise' in r and r['exercise']:
            r['exercise'] = normalize_exercise(r['exercise'])
    return pd.DataFrame(rows)

# In-memory aggregation
@st.cache_data
def aggregate_data(df_raw, rm_formula="Epley"):
    if df_raw is None or df_raw.empty:
        return pd.DataFrame()

    df = df_raw.copy()

    # Make sure the columns we expect actually exist
    for col in ["date", "program", "exercise", "weight_kg", "reps", "time_sec", "volume", "set_no"]:
        if col not in df.columns:
            df[col] = pd.NA

    # Type coercion
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["reps"] = pd.to_numeric(df["reps"], errors="coerce")
    df["weight_kg"] = pd.to_numeric(df["weight_kg"], errors="coerce")
    df["time_sec"] = pd.to_numeric(df["time_sec"], errors="coerce")
    df["volume"] = pd.to_numeric(df["volume"], errors="coerce")

    # ---- 1RM calculation ----
    def brzycki(row):
        w = row.get("weight_kg")
        r = row.get("reps")
        if pd.isna(w) or pd.isna(r) or r <= 0:
            return None
        return w / (1.0278 - 0.0278 * r)

    if rm_formula == "Epley":
        df["estimated_1rm"] = df.apply(
            lambda row: calculate_epley_1rm(row["weight_kg"], row["reps"])
            if not (pd.isna(row["weight_kg"]) or pd.isna(row["reps"]))
            else None,
            axis=1,
        )
    elif rm_formula == "Brzycki":
        df["estimated_1rm"] = df.apply(brzycki, axis=1)
    else:
        df["estimated_1rm"] = pd.NA

    # ---- Group + aggregate ----
    grouped = df.groupby(["date", "program", "exercise"], dropna=False)

    daily_summary = grouped.agg(
        max_1rm=("estimated_1rm", "max"),
        best_weight_kg=("weight_kg", "max"),
        total_volume=("volume", "sum"),
        num_sets=("set_no", "count"),
        max_time_sec=("time_sec", "max"),
    ).reset_index()

    # ---- Best reps (for the heaviest set) ----
    def get_best_reps(g: pd.DataFrame):
        # If column missing somehow, just bail
        if "weight_kg" not in g.columns or "reps" not in g.columns:
            return None
        g_nonan = g.dropna(subset=["weight_kg"])
        if g_nonan.empty:
            return None
        # row with max weight_kg
        idx = g_nonan["weight_kg"].idxmax()
        # idx might not exist in extreme edge-cases; be paranoid
        if idx not in g_nonan.index:
            return None
        return g_nonan.loc[idx, "reps"]

    try:
        best_reps_df = grouped.apply(get_best_reps).reset_index(name="best_reps")
        daily_summary = pd.merge(
            daily_summary,
            best_reps_df,
            on=["date", "program", "exercise"],
            how="left",
        )
    except Exception as e:
        # If anything goes sideways here, don't kill the app – just skip best_reps
        daily_summary["best_reps"] = None
        # You can log e somewhere if you want

    return daily_summary[
        [
            "date",
            "program",
            "exercise",
            "num_sets",
            "max_1rm",
            "best_weight_kg",
            "best_reps",
            "total_volume",
            "max_time_sec",
        ]
    ]

    
# Main app  UI
st.set_page_config(page_title="Workout Log Analyzer", layout="wide")
st.title("Workout Log Analyzer")
st.markdown("Upload or select workout logs to parse, aggregate, and visualize trends.")

# Sidebar settings
with st.sidebar:
    st.header("Settings")
    conf_threshold = st.slider("ML Confidence Threshold", 0.0, 1.0, 0.60, 0.05)
    rm_formula = st.selectbox("1RM Formula", ["Epley", "Brzycki"])
    smoothing_window = st.slider("Plot Smoothing Window (days)", 1, 30, 7)

# Choose input mode
mode = st.radio(
    "Input Mode",
    ["Upload single file", "Select from data_raw", "Upload multiple files"],
    horizontal=True,
)

text_files = None
source_names = []

# Input Handling

if mode == "Upload single file":
    uploaded = st.file_uploader("Upload a log file", type='txt')
    if uploaded:
        text_files = [uploaded]
        source_names = [uploaded.name]

elif mode == "Select from data_raw":
    if not RAW_DATA_DIR.exists():
        st.error(f"Directory not found: {RAW_DATA_DIR}")
    else:
        files = sorted([f for f in RAW_DATA_DIR.glob("*.txt")])
        if not files:
            st.warning("No .txt files found in data_raw")
        else:
            chosen = st.selectbox("Choose file", [f.name for f in files])
            if chosen:
                path = RAW_DATA_DIR / chosen
                text_files = [path.open('r', encoding="utf-8").read()]
                source_names = [chosen]

elif mode == "Upload multiple files":
    text_files = st.file_uploader(
        "Drag & drop many .txt files here",
        type="txt",
        accept_multiple_files=True)
    if text_files:
        source_names = [f.name for f in text_files]

# Processing
if text_files and st.button("Process Files", type="primary"):
    with st.spinner(f"Parsing {len(text_files)} file(s)..."):
        load_ml_model() # early trigger if file missing

        all_rows = []
        for i, file in enumerate(text_files):
            content = file.read().decode("utf-8") if hasattr(file, "read") else file
            df = parse_file_content(content, source_names[i], conf_threshold)
            all_rows.extend(df.to_dict("records"))

        if not all_rows:
            st.error("No sets were parsed. Check your log format.")
            st.stop()

        df_raw = pd.DataFrame(all_rows)
        df_agg = aggregate_data(df_raw, rm_formula)

        # Store in session state for plots
        st.session_state.df_agg = df_agg
        st.session_state.df_raw = df_raw

        st.success(f"Sucessfully parsed {len(df_raw)} sets from {len(text_files)} file(s).")

# Display Results 

if "df_agg" in st.session_state:
    df_agg = st.session_state.df_agg
    df_raw = st.session_state.df_raw

    tab1, tab2, tab3, tab4 = st.tabs(["Daily Summary", "Raw Sets", "Trends", "Downloads"])

    with tab1:
        st.dataframe(df_agg, use_container_width=True)
    
    with tab2:
        st.dataframe(df_raw, use_container_width=True)
    
    with tab3:
        exercises = sorted(df_agg["exercise"].dropna().unique())
        selected_ex = st.selectbox("Select Exercise", exercises, index=0)

        plot_df = df_agg[df_agg["exercise"] == selected_ex].copy()
        plot_df = plot_df.sort_values("date")
        plot_df["1rm_smooth"] = plot_df["max_1rm"].rolling(smoothing_window, min_periods=1).mean()
        plot_df["weight_smooth"] = plot_df["best_weight_kg"].rolling(smoothing_window, min_periods=1).mean()

        col1, col2 = st.columns(2)
        with col1:
            fig = px.line(
                plot_df,
                x="date",
                y=["max_1rm", "1rm_smooth"],
                title=f"Estimated 1RM - {selected_ex}",
                markers=True,
            )
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.line(
                plot_df,
                x="date",
                y=["best_weight_kg", "weight_smooth"],
                title = f"Best Weight - {selected_ex}",
                markers = True,
            )
            st.plotly_chart(fig, use_container_width=True)
        
        fig_vol = px.bar(
            plot_df,
            x="date",
            y="total_volume",
            title = f"Volume - {selected_ex}",
        )
        st.plotly_chart(fig_vol, use_container_width=True)

    with tab4:
        st.download_button(
            "Download Daily Summary CSV",
            df_agg.to_csv(index=False).encode(),
            "workout_history_daily.csv",
            "text/csv",
        )
        st.download_button(
            "Download Raw Sets CSV",
            df_raw.to_csv(index=False).encode(),
            "workout_raw_sets.csv",
            "text/csv",
        )

# LOW CONFIDENCE LINES
if TO_REVIEW_PATH.exists():
    with st.expander("Review Low-confidence lines", expanded=False):
        review_df = pd.read_csv(TO_REVIEW_PATH)
        st.dataframe(review_df)

st.info("Throw all your logs here & see your real progress ")
