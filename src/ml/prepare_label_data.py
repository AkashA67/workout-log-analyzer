import os
import glob
import sys
import pandas as pd
from typing import List

# Define paths
PROJECT_ROOT = r"C:\Users\aakas\Documents\workout_project"
sys.path.append(PROJECT_ROOT)
RAW_DATA_PATH = os.path.join(PROJECT_ROOT, 'data_raw', '*.txt')
OUTPUT_PATH = os.path.join(PROJECT_ROOT, 'data_labels', 'lines_for_manual_labeling.csv')

def extract_unique_lines() -> List[str]:
    """
    Reads all text files in data_raw, extracts every single line,
    strips whitespace, and returns a list of unique lines.
    """
    print("Starting extraction of unique lines from raw logs...")
    all_raw_lines = set()
    
    log_files = glob.glob(RAW_DATA_PATH)
    
    if not log_files:
        print("ERROR: No .txt files found in data_raw directory.")
        return []
        
    for file_path in log_files:
        try:
            with open(file_path, 'r', encoding='UTF-8') as f:
                # Read all lines, strip leading/trailing whitespace, and add to set
                lines = [line.strip() for line in f if line.strip()]
                all_raw_lines.update(lines)
                
        except Exception as e:
            print(f"Error reading file {os.path.basename(file_path)}: {e}")
            
    print(f"Extracted {len(all_raw_lines)} unique lines across {len(log_files)} files.")
    return sorted(list(all_raw_lines))


def run_label_preparation():
    # 1. Extract all unique lines
    unique_lines = extract_unique_lines()
    
    if not unique_lines:
        return

    # 2. Create DataFrame with required columns
    # We only create a DataFrame from the raw lines
    df_labels = pd.DataFrame({'raw_line': unique_lines, 'label': '', 'Rationale': ''})
    
    # 3. Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    # 4. Save to CSV
    df_labels.to_csv(OUTPUT_PATH, index=False)
    
    print(f"\n Label preparation complete! File saved to:\n{OUTPUT_PATH}")
    print("\nNext step: Manually label the 'label' column with categories (SET, EXERCISE, DATE, etc.).")


if __name__ == '__main__':
    run_label_preparation()