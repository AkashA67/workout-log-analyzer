import pandas as pd
import numpy as np
import os
from typing import Optional
from pathlib import Path


def calculate_epley_1rm(weight: Optional[float], reps: Optional[int]) -> Optional[float]:

    # The Estimated one-rep max (1RM) using the  Epley formula. 1RM = Weight * (1 + Reps/30)

    if weight is None or pd.isna(weight) or reps is None or pd.isna(reps) or reps == 0:
        return np.nan
    
    if isinstance(reps, str):
        try:
            reps = int(reps)
        except ValueError:
            return np.nan
    
    return round(weight * (1 + reps / 30.0), 0)

def get_best_reps_for_max_weight(df: pd.DataFrame) -> Optional[int]:

    max_weight = df['weight_kg'].max()

    if pd.isna(max_weight):
        return np.nan
    
    max_weight_sets = df[df['weight_kg'] == max_weight]

    reps_numeric = pd.to_numeric(max_weight_sets['reps'], errors ='coerce')

    if reps_numeric.empty:
        return np.nan
    
    return reps_numeric.max()

def run_feature_engineering():

    PROJECT_ROOT = Path(r"C:\Users\aakas\Documents\workout_project")
    RAW_SETS_PATH = PROJECT_ROOT / 'data_processed' / 'workouts_raw_sets.csv'
    DAILY_SUMMARY_PATH = PROJECT_ROOT / 'data_processed' /'workouts_daily_exercise.csv'

    try:
        df = pd.read_csv(RAW_SETS_PATH)
    except FileNotFoundError:
        print(f"Error: Input file not found at {RAW_SETS_PATH}")
        return
    
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    df['reps'] = pd.to_numeric(df['reps'], errors = 'coerce')

    df['estimated_1rm'] = df.apply(
        lambda row: calculate_epley_1rm(row['weight_kg'], row['reps']),
        axis = 1
    )

    # Grouping and Aggregation

    grouped = df.groupby(['date', 'program', 'exercise'])

    daily_summary = grouped.agg(

        max_1rm = ('estimated_1rm', 'max'),

        max_weight_kg = ('weight_kg', 'max'),

        total_volume = ('volume', 'sum'),

        num_sets = ('set_no', 'count'),

        max_time_sec = ('time_sec', 'max')

    ).reset_index()

    best_reps_df = grouped.apply(get_best_reps_for_max_weight).reset_index()

    best_reps_df.rename(columns={best_reps_df.columns[-1]: 'best_reps'}, inplace=True)

    daily_summary = pd.merge( daily_summary,
                              best_reps_df,
                              on=['date', 'program', 'exercise'],
                              how='left'
                             )

    daily_summary.rename(columns={'max_weight_kg': 'best_weight_kg'}, inplace=True)

    daily_summary = daily_summary[['date', 'program', 'exercise', 'num_sets', 'max_1rm', 
                                   'best_weight_kg', 'best_reps', 'total_volume', 'max_time_sec']]
    
    print(f"Successfully created daily summary table: {len(daily_summary)} rows.")


    os.makedirs(os.path.dirname(DAILY_SUMMARY_PATH), exist_ok=True)
    daily_summary.to_csv(DAILY_SUMMARY_PATH, index=False)


if __name__ == '__main__':
    run_feature_engineering()

