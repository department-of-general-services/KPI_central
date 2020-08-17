WITH valid_wrs AS (
    SELECT wr_id,
        dateadd(month, datediff(month, 0, date_requested), 0) AS opened_calendar_month,
        dateadd(month, datediff(month, 0, date_closed), 0) AS closed_calendar_month
    FROM afm.wrhwr
    WHERE prob_type IS NOT NULL
        AND prob_type != 'TEST(DO NOT USE)'
),
grouped_by_open_date AS (
    SELECT COUNT(*) as opened,
        opened_calendar_month
    FROM valid_wrs
    GROUP BY opened_calendar_month
),
grouped_by_close_date AS (
    SELECT COUNT(*) as closed,
        closed_calendar_month
    FROM valid_wrs
    GROUP BY closed_calendar_month
)
SELECT CAST(opened_calendar_month AS DATE) AS calendar_month,
    opened,
    closed
FROM grouped_by_open_date o
    INNER JOIN grouped_by_close_date c ON o.opened_calendar_month = c.closed_calendar_month
ORDER BY calendar_month