WITH valid_wrs AS (
    SELECT *
    FROM afm.wrhwr
    WHERE prob_type IS NOT NULL
        AND prob_type != 'TEST (DO NOT USE)'
        /* AND date_requested >= '01-01-2017' */
),
completion_data AS (
    SELECT wr_id,
        dateadd(month, datediff(month, 0, date_requested), 0) AS calendar_month,
        DATEDIFF(day, date_requested, date_completed) AS time_to_completion,
        CASE
            WHEN DATEDIFF(day, date_requested, date_completed) < 30 THEN 1
            ELSE 0
        END AS completed_in_30_days
    FROM valid_wrs
)
SELECT CAST(calendar_month AS DATE),
    CAST(SUM(completed_in_30_days) AS DECIMAL) / COUNT(*) AS percent_completed_in_30_days,
    COUNT(*) as wr_volume
FROM completion_data
GROUP BY calendar_month
ORDER BY calendar_month