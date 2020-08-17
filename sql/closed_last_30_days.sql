WITH valid_wrs AS (
    SELECT *
    FROM afm.wrhwr
    WHERE prob_type IS NOT NULL
        AND prob_type != 'TEST(DO NOT USE)'
)
SELECT COUNT(*) as count_opened
FROM valid_wrs
WHERE date_closed >= dateadd(day, - 30, getdate())