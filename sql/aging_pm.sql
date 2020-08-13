WITH
    valid_wrs
    AS
    (
        SELECT
            *
        FROM
            afm.wrhwr
        WHERE
        prob_type IS NOT NULL
            AND prob_type != 'TEST(DO NOT USE)'
    )
SELECT
    '30 days' as time_period,
    COUNT(*) as aging_pm
FROM
    valid_wrs
WHERE
date_requested < dateadd(day, - 30, getdate())
    AND prob_type IN ('PREVENTIVE MAINT', 'HVAC|PM')
    AND status IN ('AA', 'A', 'I')

