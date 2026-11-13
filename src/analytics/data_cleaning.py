import pandas as pd
import numpy as np

def clean_microclimate_data(df):
    """
    Day 2: Data cleaning & preprocessing for AtmoSync MicroClimate Arbitrage Analytics.
    """
    # 1. Remove duplicate rows
    df = df.drop_duplicates()

    # 2. Standardize timestamp format if present
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df = df.dropna(subset=['timestamp'])

    # 3. Fill missing numeric values with column median
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())

    return df

def generate_analytics_summary(df):
    """
    Generates basic statistical summary for weather & energy metrics.
    """
    summary = df.describe()
    return summary

if __name__ == "__main__":
    # Sample dataset simulation until Kaggle CSV is linked
    sample_data = pd.DataFrame({
        'timestamp': ['2026-11-12 10:00:00', '2026-11-12 11:00:00', '2026-11-12 11:00:00', '2026-11-12 12:00:00'],
        'temperature_c': [28.5, 30.2, 30.2, np.nan],
        'humidity_pct': [65.0, 60.0, 60.0, 58.0],
        'energy_demand_mw': [450.0, 480.0, 480.0, 510.0]
    })

    cleaned_df = clean_microclimate_data(sample_data)
    print("AtmoSync Day 2: Cleaned MicroClimate Data:")
    print(cleaned_df)
    print("\nSummary Statistics:")
    print(generate_analytics_summary(cleaned_df))
