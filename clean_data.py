import os
import glob
import numpy as np
import pandas as pd

RAW_DIR = os.path.join("data", "raw")
PROCESSED_DIR = os.path.join("data", "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)

def find_file_by_keyword(keyword):
    files = glob.glob(os.path.join(RAW_DIR, "*.csv"))
    for f in files:
        if keyword.lower() in os.path.basename(f).lower():
            return f
    return None

def clean_pipeline():
    print("--- Starting Day 2 Data Cleaning Pipeline ---")
    
    # 1. Clean NAV History
    nav_file = find_file_by_keyword("nav_history")
    if nav_file:
        print(f"Cleaning NAV History: {os.path.basename(nav_file)}...")
        df_nav = pd.read_csv(nav_file)
        df_nav['date'] = pd.to_datetime(df_nav['date'])
        df_nav = df_nav.sort_values(['amfi_code', 'date']).drop_duplicates(subset=['amfi_code', 'date'])
        df_nav = df_nav[df_nav['nav'] > 0]
        
        # Forward-fill missing NAV records for holidays/weekends per fund scheme
        filled_list = []
        for code, group in df_nav.groupby('amfi_code'):
            group = group.set_index('date')
            idx = pd.date_range(start=group.index.min(), end=group.index.max(), freq='D')
            group = group.reindex(idx)
            group['amfi_code'] = code
            group['nav'] = group['nav'].ffill()
            filled_list.append(group.reset_index().rename(columns={'index': 'date'}))
        df_nav_clean = pd.concat(filled_list)
        df_nav_clean.to_csv(os.path.join(PROCESSED_DIR, "cleaned_nav_history.csv"), index=False)
        print("✓ NAV History successfully forward-filled and cleaned.")
    
    # 2. Clean Investor Transactions
    tx_file = find_file_by_keyword("transaction")
    if tx_file:
        print(f"Cleaning Investor Transactions: {os.path.basename(tx_file)}...")
        df_tx = pd.read_csv(tx_file)
        
        # Standardize transaction types
        tx_mapping = {'sip': 'SIP', 'lumpsum': 'Lumpsum', 'redemption': 'Redemption', 'purchase': 'Lumpsum', 'buy': 'Lumpsum', 'sell': 'Redemption'}
        if 'transaction_type' in df_tx.columns:
            df_tx['transaction_type'] = df_tx['transaction_type'].astype(str).str.strip().str.lower().map(tx_mapping).fillna('Lumpsum')
        
        # Validate rules
        if 'amount' in df_tx.columns:
            df_tx = df_tx[df_tx['amount'] > 0]
        if 'date' in df_tx.columns:
            df_tx['date'] = pd.to_datetime(df_tx['date'])
        if 'kyc_status' in df_tx.columns:
            df_tx['kyc_status'] = df_tx['kyc_status'].astype(str).str.strip().str.upper().replace({'Y': 'VERIFIED', 'YES': 'VERIFIED', 'N': 'PENDING', 'NO': 'PENDING'})
            
        df_tx.to_csv(os.path.join(PROCESSED_DIR, "cleaned_investor_transactions.csv"), index=False)
        print("✓ Investor Transactions standardized and validated.")

    # 3. Clean Scheme Performance
    perf_file = find_file_by_keyword("performance")
    if perf_file:
        print(f"Cleaning Scheme Performance: {os.path.basename(perf_file)}...")
        df_perf = pd.read_csv(perf_file)
        
        # Coerce numeric entries and flag expense ratio ranges
        for col in df_perf.columns:
            if 'return' in col.lower() or 'ratio' in col.lower() or 'pct' in col.lower():
                df_perf[col] = pd.to_numeric(df_perf[col], errors='coerce')
        
        df_perf = df_perf.dropna(subset=['amfi_code'])
        df_perf.to_csv(os.path.join(PROCESSED_DIR, "cleaned_scheme_performance.csv"), index=False)
        print("✓ Scheme Performance numeric transformations completed.")

    # 4. Pass-through processing for all remaining supplementary datasets
    for f in glob.glob(os.path.join(RAW_DIR, "*.csv")):
        fname = os.path.basename(f)
        if not any(k in fname.lower() for k in ["nav_history", "transaction", "performance"]):
            df_orig = pd.read_csv(f)
            df_orig.drop_duplicates().to_csv(os.path.join(PROCESSED_DIR, f"cleaned_{fname}"), index=False)
            
    print("All datasets processed and saved to data/processed/ folder!")

if __name__ == "__main__":
    clean_pipeline()