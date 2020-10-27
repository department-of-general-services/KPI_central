SELECT
    calendar_month,
    count_closed / count_opened AS pct_closed
FROM
    (
        SELECT
            calendar_month,
            CAST(COUNT(*) AS DECIMAL) AS count_opened,
            CAST(SUM(is_closed) AS DECIMAL) AS count_closed
        FROM
            (
                SELECT
                    CONVERT(
                        VARCHAR(7),
                        DateAdd(month, DateDiff(month, 0, date_requested), 0),
                        120
                    ) AS calendar_month,
                    CASE
                        WHEN status = 'Clo' THEN 1
                        ELSE 0
                    END AS 'is_closed'
                FROM
                    (
                        SELECT
                            *
                        FROM
                            DGS_Archibus.afm.wrhwr
                        WHERE
                            status NOT IN ('Can', 'R', 'Rej')
                    ) wr_filtered
                WHERE
                    prob_type IS NOT NULL
                    AND date_requested >= DateAdd(month, -6, DateAdd(year, -2, getDate()))
                    AND date_requested < DateAdd(year, -2, getDate())
            ) ungrouped
        GROUP BY
            calendar_month
    ) grouped