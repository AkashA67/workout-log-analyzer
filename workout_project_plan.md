**Phase 0 — Prep (one-time)**

Gather your messy logs into data\_raw/ (keep originals).

Create a Git repo and this structure:

workout-project/

├─ data\_raw/

├─ data\_processed/

├─ notebooks/

├─ src/

│  ├─ parsers/

│  ├─ ml/

│  ├─ etl.py

│  └─ utils.py

├─ models/

├─ apps/

│  └─ streamlit\_app.py

├─ visualizations/

├─ README.md

└─ requirements.txt


Init Git, add .gitignore, README.md skeleton, requirements.txt (pandas, scikit-learn, joblib, matplotlib/plotly, streamlit).


Deliverable: Repo created + raw files placed.


**Phase 1 — Robust Rule-based Parser (MVP)**

Goal: Reliable extraction for most lines.


Steps:

Implement src/parsers/v1\_parser.py (use regex heuristics you already have).

Input: a .txt file. Output: list of rows {date, program, exercise, set\_no, weight\_kg, reps, notes}.

Implement src/parsers/dispatcher.py to detect file format and call appropriate parser.


Create src/etl.py to read all data\_raw/\*.txt, run parser(s), and write a combined CSV to data\_processed/workouts\_raw\_sets.csv.

Add basic unit tests (small .txt examples → expected CSV rows).

What to show:

A printed sample CSV and a one-file parsing demo in a Jupyter notebook.

**Skills shown:** Regex, file I/O, basic pipeline, testing.

**Deliverable:** workouts\_raw\_sets.csv + notebook demonstrating parsing.

**Phase 2 — Minimal Aggregation \& Feature Engineering**

Goal: Turn per-set rows into per-exercise/day summary rows used for analytics.

Steps:

Create src/feature\_engineering.py:

Group by date + exercise and compute:

best\_weight = max(weight)

best\_reps = reps associated with best\_weight (choose highest reps if tie)

estimated\_1RM (Epley: w\*(1+r/30))

total\_volume = sum(weight\*reps)

num\_sets

Output data\_processed/workouts\_daily\_exercise.csv.

Notebook with examples: show per-exercise dataframe and sanity checks (no NaNs, sample rows).

What to show:

A table for an exercise across dates and computed 1RM/time.

Skills shown: Pandas aggregation, feature engineering.

Deliverable: workouts\_daily\_exercise.csv + notebook.

**Phase 3 — Small ML Line-classifier (Hybrid)**

Goal: Handle format drift; label ambiguous lines automatically.

Steps:

Make a labeling CSV data\_labels/lines\_to\_label.csv. Label ~300 lines (DATE/SECTION/EXERCISE/SET/NOTE/OTHER).

Implement src/ml/train\_line\_classifier.py:

Pipeline: TfidfVectorizer (char n-grams) + LogisticRegression.

Save model to models/line\_clf.joblib.

Output evaluation metrics: accuracy, confusion matrix. (Log them)

Integrate classifier in src/parsers/dispatcher.py as fallback: try rules → if no match, call ML.

Implement active learning helper: push low-confidence predictions to data\_labels/to\_review.csv.

What to show:

Classification report and confusion matrix.

Example where ML fixes a weird format that rules missed.

Skills shown: ML pipeline, model evaluation, deployment in pipeline.

Deliverable: models/line\_clf.joblib, labeled dataset, evaluation notebook.

**Phase 4 — Database \& Query Layer**

Goal: Store cleaned data in SQLite for queries and to show SQL skills.

Steps:

Create src/db.py to:

Create SQLite DB data\_processed/workouts.db.

Tables: sets\_raw, daily\_exercise.

Functions to bulk insert CSVs.

Add example SQL queries:

Top 10 exercises by volume.

Last 12 weeks best 1RM per exercise.

Save query outputs as CSV and show sample SELECT queries in README.

What to show:

A screenshot or notebook of SQL queries and outputs.

Skills shown: SQL, ETL to DB, schema design.

Deliverable: workouts.db + sample queries.

**Phase 5 — Analysis \& Visualizations (Portfolio Gold)**

Goal: Create polished charts and insights.

Plots to make (for each important exercise):

1RM vs Date (line chart with moving average).

Best weight vs Date (line + scatter).

Weekly total volume (bar chart).

Exercise frequency heatmap (exercise × week).

Notes overlay (markers for days with “failure/dizzy/sick”).

Implementation:

Notebook notebooks/analysis.ipynb and save PNGs to visualizations/.

Use Plotly for interactive charts or Matplotlib/Seaborn for static.

What to show:

3–5 clean images embedded in README, with short captions: “What it shows” + one actionable insight.

Skills shown: EDA, visualization, storytelling.

Deliverable: visualizations/ images + notebook.

**Phase 6 — Streamlit Dashboard (Demo app)**

Goal: Interactive product to demo in interviews.

Features:

Upload .txt or choose file from repo.

Run parsing + ML classifier live.

Show parsed table preview.

Show plots (1RM trend, best weight trend).

Export cleaned CSV.

Optional: small settings panel (1RM formula choice, smoothing window).

Implementation:

app/streamlit\_app.py with caching and model loading from models/.

Host locally or use Streamlit Cloud for a public demo link.

What to show:

Short screen-recorded demo (30–60s) and link in README.

Skills shown: Productization, UX, deployment.

Deliverable: Streamlit app code + demo gif/link.

**Phase 7 — Documentation \& Presentation**

Goal: Make it interview-proof.

README should include:

Project title \& 1-line summary.

Tech stack.

Architecture diagram (tiny ASCII or image).

How to run (install, run ETL, run Streamlit).

Key files and what they do.

Link to demo (Streamlit) and GIFs of graphs.

Resume-ready bullets (copy-paste).

Example resume bullets you can use:

“Built a hybrid text-parsing + ML pipeline to extract structured training data from messy logs; processed 6 months of logs into a SQL database and produced interactive 1RM trend visualizations using Streamlit.”

“Trained a TF-IDF + LogisticRegression line classifier to handle format drift; implemented active learning for continual model improvement.”

Deliverable: Polished README + README screenshots/gifs.

Extra polish ideas (if you want to go hard)

Add Dockerfile (containerize the app).

Add CI (GitHub Actions) to run tests on push.

Add a simple web frontend instead of Streamlit (React + small backend) if you want full-stack flex.

Add a short blog post (Markdown) explaining problems faced and solutions.

Skills shown: DevOps, CI, full-stack.

**Quick Implementation Sequence (one-liner roadmap)**

**Parser MVP → 2. Aggregation → 3. Small ML classifier → 4. DB load → 5. Visual analysis notebook → 6. Streamlit app → 7. README + demo GIFs.**

Final tips — what to say in interviews

Explain the problem: real-world logs change format; need robust pipeline.
Explain the solution: hybrid rules + ML; feature engineering; dashboard.

Walk them through one technical decision (e.g., why TF-IDF char n-grams; why Epley 1RM).

Show results/visuals, then show code/architecture, then mention next steps you’d implement with more time.
