import pandas as pd
import numpy as np


def generate_microclimate_eda(df: pd.DataFrame) -> dict:
    """Compute exploratory summary and arbitrage spread metrics for AtmoSync."""
    summary = {
        "total_records": len(df),
        "missing_values": df.isnull().sum().to_dict(),
        "numeric_stats": df.describe().round(2).to_dict(),
    }
    if {"local_temp_c", "regional_temp_c"}.issubset(df.columns):
        df["temp_spread_c"] = (df["local_temp_c"] - df["regional_temp_c"]).round(2)
        summary["max_temp_spread_c"] = float(df["temp_spread_c"].max())
        summary["mean_temp_spread_c"] = float(df["temp_spread_c"].mean())
    return summary


if __name__ == "__main__":
    sample_data = pd.DataFrame({
        "zone": ["Zone-A", "Zone-B", "Zone-C"],
        "local_temp_c": [31.5, 29.0, 34.2],
        "regional_temp_c": [28.0, 27.5, 29.8],
        "energy_demand_kwh": [420.5, 390.0, 510.2],
    })
    report = generate_microclimate_eda(sample_data)
    print("AtmoSync EDA Summary:", report)
