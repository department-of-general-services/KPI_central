WITH
    valid_wrs
    AS
    (
        SELECT *
        FROM afm.wrhwr
        WHERE prob_type IS NOT NULL
            AND prob_type != 'TEST(DO NOT USE)'
    )
    SELECT '30 days' AS time_period, count(*) AS backlog
    FROM valid_wrs
    WHERE date_requested >= dateadd(day, - 30, getdate())
UNION
    SELECT '60 days' AS time_period, count(*) AS backlog
    FROM valid_wrs
    WHERE date_requested >= dateadd(day, - 60, getdate())
UNION
    SELECT '90 days' AS time_period, count(*) AS backlog
    FROM valid_wrs
    WHERE date_requested >= dateadd(day, - 90, getdate())