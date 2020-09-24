SELECT r.fkTank_ID AS Tank_ID,
    r.Fuel_Level,
    t.Tank_Number,
    s.Site_Name,
    f.Fuel AS Fuel_type,
    CAST(TIME AS DATE) AS Date,
    Time
FROM DPW_WardFuel.dbo.TLS_Readings r
    INNER JOIN DPW_WardFuel.dbo.Tanks t on r.fkTank_ID = t.Tank_ID
    INNER JOIN DPW_WardFuel.dbo.Sites s on t.fkSite_ID = s.Site_ID
    INNER JOIN DPW_WardFuel.dbo.Fuels f on t.fkFuel_ID = f.Fuel_ID
WHERE fkTank_ID = 30
    AND Time > '2020-01-01'
ORDER BY Time