import os
import glob
import pandas as pd
from sqlalchemy import create_engine, text

DB_PATH = "bluestock_mf.db"
PROCESSED_DIR = os.path.join("data", "processed")
engine = create_engine(f"sqlite:///{DB_PATH}")

def build_and_load():
    print("--- Initializing Expanded Star Schema Database Engine ---")
    
    # 1. Drop old tables and build the accurate database layout
    schema_sql = """
    DROP TABLE IF EXISTS fact_nav;
    DROP TABLE IF EXISTS fact_transactions;
    DROP TABLE IF EXISTS fact_performance;
    DROP TABLE IF EXISTS dim_fund;
    DROP TABLE IF EXISTS dim_date;

    CREATE TABLE dim_fund (
        amfi_code INTEGER PRIMARY KEY,
        fund_house TEXT,
        scheme_name TEXT,
        category TEXT,
        sub_category TEXT,
        plan TEXT,
        fund_manager TEXT
    );

    CREATE TABLE dim_date (
        date TEXT PRIMARY KEY,
        year INTEGER,
        month INTEGER,
        quarter INTEGER,
        day INTEGER,
        day_of_week TEXT
    );

    CREATE TABLE fact_nav (
        nav_id INTEGER PRIMARY KEY AUTOINCREMENT,
        amfi_code INTEGER,
        date TEXT,
        nav REAL,
        FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
        FOREIGN KEY (date) REFERENCES dim_date(date)
    );

    CREATE TABLE fact_transactions (
        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        investor_id TEXT,
        transaction_date TEXT,
        amfi_code INTEGER,
        transaction_type TEXT,
        amount_inr REAL,
        state TEXT,
        city TEXT,
        city_tier TEXT,
        age_group TEXT,
        gender TEXT,
        annual_income_lakh REAL,
        payment_mode TEXT,
        kyc_status TEXT,
        FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
        FOREIGN KEY (transaction_date) REFERENCES dim_date(date)
    );

    CREATE TABLE fact_performance (
        performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
        amfi_code INTEGER,
        return_1y REAL,
        return_3y REAL,
        return_5y REAL,
        expense_ratio REAL,
        FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
    );
    """
    
    with engine.connect() as conn:
        for statement in schema_sql.split(";"):
            if statement.strip():
                conn.execute(text(statement))
        conn.commit()
    print("✓ SQL Star Schema structure initialized inside SQLite database.")

    # 2. Populate Dimensions and Facts
    master_file = glob.glob(os.path.join(PROCESSED_DIR, "*master*.csv"))[0]
    df_master = pd.read_csv(master_file)
    df_fund_dim = df_master[['amfi_code', 'fund_house', 'scheme_name', 'category', 'sub_category', 'plan', 'fund_manager']].drop_duplicates()
    df_fund_dim.to_sql('dim_fund', engine, if_exists='append', index=False)
    print("✓ Loaded dim_fund dimension.")

    # 3. Process Time and Date dimension entries across datasets
    nav_file = os.path.join(PROCESSED_DIR, "cleaned_nav_history.csv")
    tx_file = os.path.join(PROCESSED_DIR, "cleaned_investor_transactions.csv")
    
    all_dates = pd.Index([])
    if os.path.exists(nav_file):
        df_nav = pd.read_csv(nav_file)
        all_dates = all_dates.union(pd.to_datetime(df_nav['date'].unique()))
    if os.path.exists(tx_file):
        df_tx = pd.read_csv(tx_file)
        if 'transaction_date' in df_tx.columns:
            all_dates = all_dates.union(pd.to_datetime(df_tx['transaction_date'].unique()))
            
    if not all_dates.empty:
        df_date = pd.DataFrame({
            'date': all_dates.strftime('%Y-%m-%d'),
            'year': all_dates.year,
            'month': all_dates.month,
            'quarter': (all_dates.month - 1) // 3 + 1,
            'day': all_dates.day,
            'day_of_week': all_dates.day_name()
        })
        df_date.drop_duplicates(subset=['date']).to_sql('dim_date', engine, if_exists='append', index=False)
        print("✓ Loaded dim_date dimension matrix.")

    # 4. Load Facts
    if os.path.exists(nav_file):
        pd.read_csv(nav_file).to_sql('fact_nav', engine, if_exists='append', index=False)
        print("✓ Loaded fact_nav metrics data.")

    if os.path.exists(tx_file):
        pd.read_csv(tx_file).to_sql('fact_transactions', engine, if_exists='append', index=False)
        print("✓ Loaded fact_transactions metric records.")

    perf_file = os.path.join(PROCESSED_DIR, "cleaned_scheme_performance.csv")
    if os.path.exists(perf_file):
        df_perf = pd.read_csv(perf_file)
        # Dynamically align columns present to avoid any mismatches
        valid_cols = ['amfi_code', 'return_1y', 'return_3y', 'return_5y', 'expense_ratio']
        df_perf_filtered = df_perf[[c for c in valid_cols if c in df_perf.columns]]
        df_perf_filtered.to_sql('fact_performance', engine, if_exists='append', index=False)
        print("✓ Loaded fact_performance summary metrics.")

    print("\nSuccess! All real data files loaded into SQLite tables perfectly.")

if __name__ == "__main__":
    build_and_load()