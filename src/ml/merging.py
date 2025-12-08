import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(r"C:\Users\aakas\Documents\workout_project")
old = pd.read_csv(PROJECT_ROOT / "data_labels" / "lines_for_trainning.csv")
new = pd.read_csv(PROJECT_ROOT / "data_labels" / "to_review.csv")

# Keep only rows you actually labeled
new = new[new['label'].notna()]

combined = pd.concat([old, new[['raw_line', 'label']]], ignore_index=True)
combined.drop_duplicates(subset='raw_line', keep='last', inplace=True)

combined.to_csv(PROJECT_ROOT / "data_labels" / "lines_for_trainning.csv", index=False)
print(f"Final training set: {len(combined)} lines")