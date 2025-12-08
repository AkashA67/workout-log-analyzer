# Workout Log Analyzer

- A robust ETL pipeline and interactive dashboard for parsing, analyzing, and visualizing messy workout logs. Extracts structured data (e.g., sets, reps, weights) from raw text files, computes features like estimated 1RM and total volume, stores in a SQLite database, and provides trends via charts. Handles format variations using a hybrid rule-based + ML approach.
- This project demonstrates end-to-end data processing: from regex parsing and ML classification to feature engineering, SQL storage, visualizations, and a deployable web app.

### Key Features

- **Parsing Pipeline**: Rule-based regex for structured lines + ML classifier (TF-IDF + Logistic Regression) for ambiguous ones. Saves low-confidence lines for review.
- Feature Engineering: Aggregates per-set data into daily summaries (e.g., max 1RM using Epley/Brzycki formulas, best weight/reps, total volume).
- Database Integration: SQLite DB for querying (e.g., top exercises by volume, 1RM trends).
- Visualizations: Interactive charts for 1RM trends, best weights, volume over time, and exercise frequency heatmaps (via Plotly/Matplotlib).
- Streamlit Dashboard: Upload logs, parse live, view tables/charts, and export CSVs. Supports ML confidence thresholds and 1RM formula selection.
- ML for Robustness: Trained classifier on ~500 labeled lines; includes active learning (flags low-confidence predictions).

### Architecture Overview
```text
workout_project/
   ├── data_raw/                           # Raw workout logs (*.txt)
   ├── data_processed/                     # Parsed CSVs and SQLite DB (workouts.db)
   ├── data_labels/                        # Labeled data for ML (lines_for_training.csv, to_review.csv)
   ├── src/                                # Core code
   │   ├── parsers/                        # Parsing logic
   │   │   ├── v1_parser.py                # Rule-based regex parser
   │   │   ├── normalize.py                # Exercise name normalization
   │   │   ├── hybrid_parse_all.py         # Dispatcher + ML integration
   │   │   ├── feature_engineering.py      # Aggregation and 1RM calculations
   │   │   └── db.py                       # SQLite schema, loading, and queries
   │   └── ml/                             # ML training
   │       └── train_line_classifier.py    # Model training and evaluation
   |       |__ prepare_label_data.py       # For data label reparing 
   |       |__ merging.py                  # merging review labels with old label
   ├── models/                             # Saved models (line_clf.joblib) and metrics
   ├── notebooks/                          # Exploratory analysis
   │   └── analysis.ipynb                  # Visualizations (1RM trends, heatmaps)
   ├── apps/                               # Web app
   │   └── streamlit_app.py                # Interactive dashboard
   ├── visualizations/                     # Saved charts (PNG/PDF)
   └── requirements.txt                    # Dependencies
```

# Setup and Usage

### Prerequisites

- **Python 3.9+** installed.
- **Clone the repo**: git clone https://github.com/AkashA67/workout_project.git .
- **Install dependencies**: pip install -r requirements.txt.

### Running the ETL Pipeline

- **Place your workout logs in data_raw/** (as .txt files).
- **Parse all logs (hybrid mode with ML)**: python src/parsers/hybrid_parse_all.py
- **Outputs**: data_processed/workouts_raw_sets.csv
- **Run feature engineering**: python src/feature_engineering.py
- **Outputs**: data_processed/workouts_daily_exercise.csv
- **Load to DB**: python src/db.py
- **Outputs**: data_processed/workouts.db (with tables: sets_raw, daily_exercise).


### Example DB queries (in src/db.py):

- **Top 10 exercises by volume**: SELECT exercise, SUM(volume) AS total_vol FROM sets_raw GROUP BY exercise ORDER BY total_vol DESC LIMIT 10;
- **1RM trend for Bench Press**: SELECT date, ROUND(max_1rm, 0) FROM daily_exercise WHERE exercise='Barbell Bench Press' ORDER BY date;

### Training the ML Classifier

- **Label data in data_labels/lines_for_training.csv** (columns: raw_line, label e.g., "EXERCISE", "SET").
- **Train**: python src/ml/train_line_classifier.py
- **Outputs**: models/line_clf.joblib, confusion matrix PNG, per-class metrics CSV.


### Running Visualizations

- **Open notebooks/analysis.ipynb in Jupyter**: jupyter notebook notebooks/analysis.ipynb
- **Generates charts in visualizations/** (e.g., 1RM trends, exercise frequency heatmap).

### Running the Streamlit Dashboard

- **Launch**: streamlit run apps/streamlit_app.py
- **Features**: Upload/select logs, parse live, view tables/charts, export CSVs.
- **Demo**: Live Demo on Streamlit Cloud
- **GIF Demo**: [Streamlit Demo](visualizations/ezgif-139bc2a769f72f70.gif)

# Results and Insights

- **Parsed 1343 sets** from **74 logs**.
- **Example Visualization**: [Estimated 1RM Trend for Barbell Bench Press](visualizations/bench_1rm.png)

- **1RM Trend Insight**: 1RM increased 20% over 12 weeks, correlating with higher volume weeks.

- **Exercise Frequency Heatmap** :[Exercise Frequency Heatmap](visualizations/exercise_freq_heatmap.png)

- **Insight**: Consistent focus on compound lifts (e.g., squats, bench) with accessory work tapering mid-program.
For more, see notebooks/analysis.ipynb.

# Project Summary

- Developed an end-to-end ETL pipeline in Python to parse unstructured workout logs using regex and a scikit-learn ML classifier (TF-IDF + Logistic Regression), achieving 95% accuracy on ambiguous lines; aggregated features like Epley 1RM and volume for trend analysis.
- Built a SQLite database for storing parsed data and wrote queries to extract insights (e.g., top exercises by volume); visualized trends with Plotly in Jupyter notebooks, revealing 15-25% strength gains over 6 months.
- Created an interactive Streamlit dashboard for log uploading, real-time parsing, and customizable visualizations (e.g., 1RM smoothing); supports ML confidence thresholds for robust handling of format variations.

### Limitations and Next Steps

- Assumes English logs with semi-consistent formats; expand ML training data for more variations.
- **Next**: Add API endpoints (Flask backend), deploy to AWS/Heroku, or integrate computer vision for image-based logs.

# Contributing

### Contributions are welcome!
- Fork this repo
- Create a new branch
- Commit your changes
- Push to your branch and open a Pull Request


# License
- This project is licensed under the MIT License — you’re free to use, modify, and distribute it.
