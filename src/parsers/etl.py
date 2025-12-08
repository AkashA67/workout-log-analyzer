import os 
import sys
import glob
import pandas as pd 
from parsers.v1_parser import parse_log_content

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
RAW_DATA_PATH = os.path.join(PROJECT_ROOT, 'data_raw', '*.txt')
PROCESSED_DATA_PATH = os.path.join(PROJECT_ROOT, 'data_processed', 'workouts_raw_sets.csv')

def run_etl():

    all_rows = []
    file_count = 0

    log_files = glob.glob(RAW_DATA_PATH)

    if not log_files:
        print('ERROR: no .txt file')
        return
    
    for file_path in log_files:
        file_count += 1
        file_name = os.path.basename(file_path)

        try:
            with open(file_path, 'r', encoding='UTF-8') as f:
                raw_content = f.read()

            rows = parse_log_content(raw_content)

            all_rows.extend(rows)

            print(f"-> Parsed {len(rows)} sets from {file_name}")
        
        except Exception as e:
            print(f"ERROR parsing file {file_name}: {e}")

    
    print(f"\nSuccessfully processed {file_count} files.")


    df = pd.DataFrame(all_rows)

    print(f"Total structured sets extracted: {len(df)}")

    os.makedirs(os.path.dirname(PROCESSED_DATA_PATH), exist_ok=True)
    df.to_csv(PROCESSED_DATA_PATH, index=False)

    print(f"ETL Complete! Data saved to {PROCESSED_DATA_PATH}")


if __name__ == '__main__':
    run_etl()