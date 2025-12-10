import glob
from pathlib import Path
import joblib
import csv
import json
import pandas as pd
from pathlib import Path

from src.parsers.v1_parser import parse_log_content
from src.parsers.normalize import normalize_exercise


CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
RAW_GLOB = PROJECT_ROOT / "data_raw" / "*.txt"
OUT_RAW_SETS = PROJECT_ROOT / "data_processed" / "workouts_raw_sets.csv"
TO_REVIEW = PROJECT_ROOT / "data_labels" / "to_review.csv"
MODEL_PATH = PROJECT_ROOT / "models" / "line_clf.joblib"

# load classifier 

clf = joblib.load(MODEL_PATH)
CONF_THRESHOLD = 0.60

def ml_label_fn(line: str):

    try:
        pred = clf.predict([line])[0]
        prob = float(clf.predict_proba([line])[0].max())
        return (str(pred), prob)
    except Exception:

        try:
            pred = clf.predict([line])[0]
            return (str(pred), 1.0)
        except Exception:
            return ("OTHER", 0.0)
        
# save low confidence lines
def save_review_fn(line: str, conf: float, src_file: str, lineno: int):
    TO_REVIEW.parent.mkdir(parents=True, exist_ok=True)
    
    write_header = not TO_REVIEW.exists()

    with open(TO_REVIEW, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["raw_line", "confidence", "source_file", "line_no"])
        writer.writerow([line, conf, src_file, lineno])

all_rows = []
for path in sorted(glob.glob(str(RAW_GLOB))):
    src = Path(path)
    raw = src.read_text(encoding="utf-8")
    rows = parse_log_content(raw, source_file=str(src.name), ml_label_fn=ml_label_fn,
                             save_review_fn=save_review_fn, conf_threshold=CONF_THRESHOLD)
    
    for r in rows:
        r["_source_file"] = src.name
        if 'exercise' in r and r['exercise']:
            r['exercise'] = normalize_exercise(r['exercise'])
    all_rows.extend(rows)
    
    


# save combined CSV
OUT_RAW_SETS.parent.mkdir(parents=True, exist_ok=True)
if all_rows:
    df = pd.DataFrame(all_rows)

    cols = ["_source_file","date","program","exercise","set_no","weight_kg","reps","time_sec","iso_load","volume","notes"]
    cols = [c for c in cols if c in df.columns] + [c for c in df.columns if c not in cols]
    df.to_csv(OUT_RAW_SETS, index=False,columns=cols)
    print(f"Wrote {len(df)} rows to {OUT_RAW_SETS}")
else:
    print("No rows parsed.")

# Save a small summary about to_review file
if TO_REVIEW.exists():
    try:
        df_review = pd.read_csv(TO_REVIEW)
        print(f"Low-confidence lines saved: {len(df_review)} to ({TO_REVIEW})")
    except:
        print(f"Review file created → {TO_REVIEW}")


