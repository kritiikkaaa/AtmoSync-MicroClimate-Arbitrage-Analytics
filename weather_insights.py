# AtmoSync: MicroClimate Arbitrage - Yogender's Analytics Script
import pandas as pd
from pathlib import Path

def generate_weather_insights():
    """
    Reads validated microclimate sensor readings and generates insights summary.
    """
    file_path = Path("data/processed/validated_sensor_readings.csv")
    
    if not file_path.exists():
        print("Validated sensor readings file not found!")
        return
        
    df = pd.read_csv(file_path)
    
    print("=== Yogender's AtmoSync Data Analytics Report ===")
    print(f"Total Validated Records Analyzed: {len(df)}")
    print(f"Average Temperature: {df['temperature_c'].mean():.2f} °C")
    print(f"Average Humidity: {df['humidity_pct'].mean():.2f} %")
    print(f"Average Soil Moisture: {df['soil_moisture_pct'].mean():.2f} %")

if __name__ == "__main__":
    generate_weather_insights()
