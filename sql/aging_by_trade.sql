WITH
    valid_wrs
    AS
    (
        SELECT *
        FROM afm.wrhwr
        WHERE prob_type IS NOT NULL
            AND prob_type != 'TEST(DO NOT USE)'
    ),
    trades
    AS
    (
        SELECT wr_id,
            prob_type AS problem_type,
            date_requested,
            CASE
        WHEN prob_type LIKE 'ELEC%'
                OR prob_type = 'OUTLETS' THEN
        'Electrical'
        WHEN prob_type IN ('PAINT', 'PAINTING') THEN
        'Painting'
        WHEN prob_type LIKE 'PLUMB%' THEN
        'Plumbing'
        WHEN prob_type IN ('CARPENTRY', 'DOOR', 'LOCK', 'WALL') THEN
        'Carpentry'
        WHEN prob_type LIKE 'HVAC%'
                OR prob_type IN ('CHILLERS', 'COOLING TOWERS') THEN
        'HVAC'
        ELSE 'None'
        END AS trade
        FROM valid_wrs
    )
SELECT trade,
    count(*) AS aging_backlog
FROM trades
WHERE trade != 'None'
    AND date_requested >= dateadd(day, - 30, getdate())
GROUP BY  trade