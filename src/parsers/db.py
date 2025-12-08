import sqlite3
import pandas as pd
from pathlib import Path

DATA_PATH = Path(r"C:\Users\aakas\Documents\workout_project\data_processed")
DB_PATH = DATA_PATH / "Workouts.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
            CREATE TABLE IF NOT EXISTS sets_raw(
              date TEXT,
              program TEXT,
              exercise TEXT,
              set_no INTEGER,
              weight_kg REAL,
              reps INTEGER,
              volume REAL,
              notes TEXT
            );
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS daily_exercise(
              date TEXT,
              exercise TEXT,
              best_weight REAL,
              best_reps INTEGER,
              max_1rm REAL,
              total_volume REAL,
              num_sets INTEGER
            );
    """)

    conn.commit()
    conn.close()

def load_csv_to_db():
    conn = sqlite3.connect(DB_PATH)

    raw = pd.read_csv(DATA_PATH / "workouts_raw_sets.csv")
    raw.to_sql("sets_raw", conn, if_exists="replace", index=False)

    daily = pd.read_csv(DATA_PATH / "workouts_daily_exercise.csv")
    daily.to_sql("daily_exercise", conn, if_exists="replace", index=False)

    conn.close()

def example_queries():
    conn = sqlite3.connect(DB_PATH)

    print("\nTop 10 exercises by volume:")
    q1 = conn.execute("""
                    SELECT exercise, 
                      SUM(volume) AS total_vol
                      FROM sets_raw
                      GROUP BY exercise 
                      ORDER BY total_vol DESC
                      LIMIT 10;
    """).fetchall()
    print(q1)

    print("\n12-week 1RM trend for Bench Press: ")
    q2 = conn.execute("""
                    SELECT date, 
                      ROUND(max_1rm, 0) AS max_1rm -- can use this for Integer onlY "CAST(ROUND(max_1rm, 0) AS INTEGER) AS max_1rm" 
                      FROM daily_exercise
                      WHERE exercise='Barbell Bench Press'
                      ORDER BY date;                   
    """).fetchall()

    print(q2)

    conn.close()


if __name__ == '__main__':
    init_db()
    load_csv_to_db()
    # example_queries()