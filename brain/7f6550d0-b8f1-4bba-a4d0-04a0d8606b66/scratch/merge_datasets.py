
import pandas as pd
import os

def merge_datasets():
    path_2024_2025 = r'c:\myproject\backend\data\datasets\energy_dataset_2024_2025.csv'
    path_50k = r'c:\myproject\backend\data\datasets\energy_dataset_50k_plus.csv'
    output_path = r'c:\myproject\backend\data\datasets\energy_dataset_merged_3years.csv'
    
    print(f"Loading {path_2024_2025}...")
    df1 = pd.read_csv(path_2024_2025)
    
    print(f"Loading {path_50k}...")
    df2 = pd.read_csv(path_50k)
    
    print("Concatenating datasets...")
    # Add both datasets as requested
    df_merged = pd.concat([df1, df2], ignore_index=True)
    
    print("Sorting by timestamp...")
    # Convert to datetime for proper sorting
    df_merged['Timestamp'] = pd.to_datetime(df_merged['Timestamp'])
    df_merged = df_merged.sort_values(by='Timestamp')
    
    # Convert back to ISO format for consistency
    df_merged['Timestamp'] = df_merged['Timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%S')
    
    print(f"Saving to {output_path}...")
    df_merged.to_csv(output_path, index=False)
    
    print("Merge complete.")
    print(f"Total rows: {len(df_merged)}")

if __name__ == "__main__":
    merge_datasets()
