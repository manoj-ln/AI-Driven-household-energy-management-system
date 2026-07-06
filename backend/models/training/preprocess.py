import pandas as pd
from pathlib import Path
import numpy as np

def preprocess_energy_data(input_path: str, output_path: str) -> None:
    # Load data
    df = pd.read_csv(input_path)
    df['timestamp'] = pd.to_datetime(df['Timestamp'])
    df = df.set_index('timestamp').sort_index()
    df = df.drop(columns=['Timestamp'])  # Drop the original string column

    # Basic time features
    df['hour'] = df.index.hour
    df['day_of_week'] = df.index.dayofweek
    df['month'] = df.index.month
    df['is_weekend'] = (df.index.dayofweek >= 5).astype(int)
    df['is_peak_hour'] = ((df.index.hour >= 18) & (df.index.hour <= 22)).astype(int)

    # Sample to reduce size
    df = df.sample(50000, random_state=42)

    # Save processed data
    df.to_csv(output_path, index=True, index_label='timestamp')
    print(f"Processed data saved to {output_path}, shape: {df.shape}")

if __name__ == "__main__":
    input_path = Path(__file__).resolve().parents[2] / "data" / "raw" / "energy_consumption.csv"
    output_path = Path(__file__).resolve().parents[2] / "data" / "processed" / "energy_features.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    preprocess_energy_data(str(input_path), str(output_path))
