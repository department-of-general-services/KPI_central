SELECT
    trade,
    count(*)
FROM
    (
        SELECT
            wr_id,
            status,
            prob_type AS problem_type,
            date_requested,
            CASE
                WHEN prob_type LIKE 'ELEC%'
                OR prob_type = 'OUTLETS' THEN 'Electrical'
                WHEN prob_type IN ('PAINT', 'PAINTING') THEN 'Painting'
                WHEN prob_type LIKE 'PLUMB%' THEN 'Plumbing'
                WHEN prob_type IN ('CARPENTRY', 'DOOR', 'LOCK', 'WALL') THEN 'Carpentry'
                WHEN prob_type LIKE 'HVAC%'
                OR prob_type IN ('CHILLERS', 'COOLING TOWERS') THEN 'HVAC Corrective'
                ELSE 'None'
            END AS trade
        FROM
            DGS_Archibus.afm.wrhwr
        WHERE
            prob_type != 'HVAC|PM'
    ) trades
WHERE
    trade != 'None'
    /*SELECT WR's that are open and older than 30 days*/
    AND date_requested < dateadd(day, - 30, getdate())
    AND status IN ('AA', 'A', 'I', 'Com')
GROUP BY
    trade