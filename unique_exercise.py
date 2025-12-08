import pandas as pd
from pathlib import Path

DATA_PATH = Path(r"C:\Users\aakas\Documents\workout_project\data_processed")
RAW_CSV = DATA_PATH / "workouts_raw_sets.csv"
OUTPUT_CSV = DATA_PATH / "unique_exercises.csv"

# Read the raw file
df = pd.read_csv(RAW_CSV)

# Change 'exercise' below if your column has a different name
# Common alternatives: 'Exercise', 'exercise_name', 'Movement', etc.
exercise_column = 'exercise'  # ← CHANGE THIS if needed!

# Get unique values, sort them nicely, and save as one column
unique_exercises = (
    df[exercise_column]
    .astype(str)
    .str.strip()
    .drop_duplicates()
    .sort_values()
    .reset_index(drop=True)
)

# Save to CSV — one exercise per row
unique_exercises.to_csv(OUTPUT_CSV, index=False, header=['exercise'])

print(f"Done! {len(unique_exercises)} unique exercises saved to:")
print(OUTPUT_CSV)
