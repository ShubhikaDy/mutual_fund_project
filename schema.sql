-- SQLite Mutual Fund Star Schema Definition
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
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);