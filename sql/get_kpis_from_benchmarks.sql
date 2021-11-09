WITH catch_unfinished_but_late
/*This query allows us to account for work that hasn't been 
 completed yet, but is already past the benchmark.*/
AS (
    SELECT *,
        CASE
            WHEN (
                date_completed IS NULL
                AND days_since_request > completion_benchmark
            ) THEN CAST(1 AS DECIMAL)
            ELSE CAST(0 AS DECIMAL)
        END AS not_completed_but_late,
        CASE
            WHEN (
                date_closed IS NULL
                AND weekdays_since_completion > closure_benchmark
            ) THEN CAST(1 AS DECIMAL)
            ELSE CAST(0 AS DECIMAL)
        END AS not_closed_but_late
    FROM [afm].[dash_benchmarks]
)
SELECT *,
    CASE
        WHEN days_to_completion <= completion_benchmark THEN CAST(1 AS DECIMAL)
        WHEN not_completed_but_late = 1 THEN CAST(0 AS DECIMAL)
        ELSE CAST(0 AS DECIMAL)
    END AS is_on_time,
    CASE
        WHEN weekdays_complete_to_close <= closure_benchmark THEN CAST(1 AS DECIMAL)
        WHEN not_completed_but_late = 1 THEN NULL
        WHEN not_closed_but_late = 1 THEN CAST(0 AS DECIMAL)
        ELSE CAST(0 AS DECIMAL)
    END AS closed_on_time,
    CASE
        WHEN primary_type IN ('PREVENTIVE_HVAC') THEN CAST(1 AS DECIMAL)
        ELSE CAST(0 AS DECIMAL)
    END AS is_ratio_pm,
    CASE
        WHEN primary_type IN ('HVAC') THEN CAST(1 AS DECIMAL)
        ELSE CAST(0 AS DECIMAL)
    END AS is_ratio_cm,
    CASE
        WHEN primary_type IN ('PREVENTIVE_HVAC', 'PREVENTIVE_GENERAL') THEN CAST(1 AS DECIMAL)
        ELSE CAST(0 AS DECIMAL)
    END AS is_any_pm
FROM catch_unfinished_but_late c
WHERE date_completed IS NOT NULL
    OR not_completed_but_late = 1;