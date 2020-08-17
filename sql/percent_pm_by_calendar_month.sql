WITH valid_wrs AS (
    SELECT wr_id,
        prob_type AS prob_type,
        date_requested
    FROM afm.wr
    WHERE prob_type IS NOT NULL
        AND prob_type != 'TEST (DO NOT USE)'
        /* limiting date because otherwise we'll get divide by zero error */
        AND date_requested >= '01-01-2017'
),
hvac_wrs AS (
    SELECT wr_id,
        dateadd(month, datediff(month, 0, date_requested), 0) AS calendar_month,
        CASE
            WHEN prob_type IN (
                'BOILER',
                'CHILLERS',
                'COOLING TOWERS',
                'HVAC INFRASTRUCTURE',
                'HVAC',
                'HVAC|HEATING OIL',
                'HVAC|INSPECTION',
                'HVAC|REPAIR',
                'HVAC|REPLACEMENT'
            ) THEN 1
            ELSE 0
        END AS is_corrective,
        CASE
            WHEN prob_type IN (
                'HVAC|PM',
                'PREVENTIVE MAINT'
            ) THEN 1
            ELSE 0
        END AS is_preventive
    FROM valid_wrs
)
SELECT CAST(calendar_month as DATE) AS calendar_month,
    SUM(is_corrective + is_preventive) AS hvac_volume,
    CAST(SUM(is_preventive) AS DECIMAL) / SUM(is_corrective + is_preventive) * 100 AS percent_preventive,
    COUNT(*) as wr_volume
FROM hvac_wrs
GROUP BY calendar_month
ORDER BY calendar_month