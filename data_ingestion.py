import os
import glob
import pandas as pd

RAW_DIR = os.path.join("data", "raw")

def explore_raw_datasets():
    print("--- TASK: Loading & Profiling Raw Datasets ---")
    # Dynamically find any CSV file sitting in data/raw
    csv_files = glob.glob(os.path.join(RAW_DIR, "*.csv"))
    
    if not csv_files:
        print("No CSV files found in data/raw/ yet. Make sure your datasets are pasted there.")
        return
        
    for file_path in csv_files:
        filename = os.path.basename(file_path)
        print(f"\n================ Profiling File: {filename} ================")
        df = pd.read_csv(file_path)
        
        # Print shape, types, and head
        print(f"Shape (Rows, Columns): {df.shape}")
        print("\nData Types:")
        print(df.dtypes)
        print("\nFirst 3 Rows:")
        print(df.head(3))
        print("-" * 50)

def evaluate_fund_data():
    print("\n--- TASK: Fund Master Exploration & Validation ---")
    master_path = os.path.join(RAW_DIR, "fund_master.csv")
    history_path = os.path.join(RAW_DIR, "nav_history.csv")
    
    if not os.path.exists(master_path) or not os.path.exists(history_path):
        print("\nNote: fund_master.csv or nav_history.csv are not in data/raw/ yet. Skipping validation step.")
        return

    fund_master = pd.read_csv(master_path)
    nav_history = pd.read_csv(history_path)

    # Count unique elements
    print(f"Unique Fund Houses: {fund_master['fund_house'].nunique() if 'fund_house' in fund_master else 'N/A'}")
    print(f"Unique Categories: {fund_master['category'].nunique() if 'category' in fund_master else 'N/A'}")
    print(f"Unique Sub-Categories: {fund_master['sub_category'].nunique() if 'sub_category' in fund_master else 'N/A'}")
    print(f"Unique Risk Grades: {fund_master['risk_grade'].nunique() if 'risk_grade' in fund_master else 'N/A'}")

    # Validate that every code in master exists in history
    if 'amfi_code' in fund_master and 'amfi_code' in nav_history:
        master_codes = set(fund_master['amfi_code'].unique())
        history_codes = set(nav_history['amfi_code'].unique())
        
        missing_in_history = master_codes - history_codes
        
        print("\n--- Data Quality Summary ---")
        if len(missing_in_history) == 0:
            print("Validation Passed: Every code in fund_master exists in nav_history.")
        else:
            print(f"Validation Warning: {len(missing_in_history)} codes in fund_master are missing from nav_history.")
    else:
        print("Could not validate codes: Check if 'amfi_code' column name matches exactly.")

if __name__ == "__main__":
    explore_raw_datasets()
    evaluate_fund_data()