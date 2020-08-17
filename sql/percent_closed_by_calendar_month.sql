WITH valid_wrs AS (
    SELECT *
    FROM afm.wrhwr
    WHERE prob_type IS NOT NULL
        AND prob_type != 'TEST (DO NOT USE)'
        /* AND date_requested >= '01-01-2017' */
),
requested_and_closed AS (
    SELECT wr_id,
        CASE
            WHEN status IN ('Com', 'Clo') THEN 1
            ELSE 0
        END AS is_closed,
        dateadd(month, datediff(month, 0, date_requested), 0) AS calendar_month
    FROM valid_wrs
)
SELECT CAST(calendar_month AS DATE),
    CAST(SUM(is_closed) AS DECIMAL) / COUNT(*) AS percent_closed,
    COUNT(*) AS wr_volume
FROM requested_and_closed
GROUP BY calendar_month
ORDER BY calendar_month