WITH valid_wrs AS (
    SELECT *
    FROM afm.wrhwr
    WHERE prob_type IS NOT NULL
        AND prob_type != 'TEST (DO NOT USE)'
        /* AND date_requested >= '01-01-2017' */
),
cost_data AS (
    SELECT wr_id,
        CASE
            WHEN cost_total > 0 THEN 1
            ELSE 0
        END AS is_cost_total_nonzero,
        CASE
            WHEN cost_labor > 0 THEN 1
            ELSE 0
        END AS is_cost_labor_nonzero,
        dateadd(month, datediff(month, 0, date_requested), 0) AS calendar_month
    FROM valid_wrs
)
SELECT CAST(calendar_month AS DATE),
    CAST(SUM(is_cost_total_nonzero) AS DECIMAL) / COUNT(*) as percent_nonzero_cost_total,
    CAST(SUM(is_cost_labor_nonzero) AS DECIMAL) / COUNT(*) as percent_nonzero_cost_labor,
    COUNT(*) as wr_volume
FROM cost_data
GROUP BY calendar_month
ORDER BY calendar_month