-- Query 1: Average NAV per month for each scheme
SELECT amfi_code, STRFTIME('%Y-%m', date) as month, AVG(nav) as avg_nav 
FROM fact_nav 
GROUP BY amfi_code, month;

-- Query 2: Total number of active records grouped by fund house
SELECT fund_house, COUNT(*) as active_funds 
FROM dim_fund 
GROUP BY fund_house;

-- Query 3: Tracking extreme NAV performance peaks per mutual fund
SELECT amfi_code, MAX(nav) as peak_nav, MIN(nav) as floor_nav 
FROM fact_nav 
GROUP BY amfi_code;

-- Query 4: Monthly historical system record row counts
SELECT STRFTIME('%Y-%m', date) as month, COUNT(*) as records_captured 
FROM fact_nav 
GROUP BY month;

-- Query 5: Funds distribution across individual strategic sub-categories
SELECT sub_category, COUNT(*) as scheme_count 
FROM dim_fund 
GROUP BY sub_category;

-- Query 6: Complete scheme directory joined with latest recorded pricing assets
SELECT f.scheme_name, f.category, n.date, n.nav 
FROM dim_fund f 
JOIN fact_nav n ON f.amfi_code = n.amfi_code 
ORDER BY n.date DESC LIMIT 10;

-- Query 7: Growth comparison of Direct vs Regular mutual fund tracking plans
SELECT plan, COUNT(*) as plan_count 
FROM dim_fund 
GROUP BY plan;

-- Query 8: Rolling average pricing indicators tracking index values
SELECT date, AVG(nav) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as weekly_rolling_avg_nav
FROM fact_nav 
LIMIT 30;

-- Query 9: Density distribution of schemes handled per unique fund manager
SELECT fund_manager, COUNT(*) as total_assigned_schemes 
FROM dim_fund 
GROUP BY fund_manager 
ORDER BY total_assigned_schemes DESC;

-- Query 10: Identify top historical date entries holding maximum transaction values
SELECT date, COUNT(*) as daily_metric_density 
FROM fact_nav 
GROUP BY date 
ORDER BY daily_metric_density DESC LIMIT 5;