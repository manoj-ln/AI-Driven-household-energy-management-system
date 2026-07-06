
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_3year_data():
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2025, 12, 31, 23, 50)
    
    # 10 minute intervals
    periods = int((end_date - start_date).total_seconds() / 600) + 1
    timestamps = [start_date + timedelta(minutes=10*i) for i in range(periods)]
    
    df = pd.DataFrame({'timestamp': [t.isoformat() for t in timestamps]})
    
    # Add time features
    df['hour'] = [t.hour for t in timestamps]
    df['day_of_week'] = [t.weekday() for t in timestamps]
    df['is_holiday'] = [1 if t.weekday() >= 5 else 0 for t in timestamps]
    
    # Simulate temperature based on month
    def get_temp(dt):
        month = dt.month
        base = 25
        if month in [3,4,5]: base = 32 # Summer
        if month in [11,12,1,2]: base = 20 # Winter
        return base + np.random.uniform(-3, 3)

    df['temperature'] = [get_temp(t) for t in timestamps]
    
    # Simulate devices (30 devices total as per DeviceLibrary)
    # Mapping to existing columns 5-134 (some are placeholders or grouped)
    # We'll generate 130 columns of device data to match original schema
    for i in range(1, 131):
        col_name = f'device_{i}'
        # Base usage + hourly pattern + random noise
        # Higher usage during day, lower at night
        usage = 0.01 + 0.02 * np.sin(np.pi * df['hour'] / 24) + np.random.normal(0, 0.005, periods)
        df[col_name] = np.maximum(0, usage)

    # Calculate total energy
    df['total_energy'] = df.iloc[:, 5:].sum(axis=1)
    
    output_path = r'c:\myproject\backend\data\datasets\energy_dataset_3_years.csv'
    df.to_csv(output_path, index=False)
    print(f"Generated 3-year dataset: {output_path}")

if __name__ == "__main__":
    generate_3year_data()
