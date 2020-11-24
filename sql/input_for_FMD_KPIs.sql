SELECT
    wr.wr_id,
    wr.date_requested,
    wr.time_requested,
    wr.date_completed,
    wr.time_completed,
    wr.date_closed,
    -- wr.cf_notes,
    wr.pmp_id,
    wr.bl_id,
    wr.cost_total,
    wr.cost_labor,
    wr.cost_parts,
    wr.prob_type AS problem_type,
    wr.requestor,
    wr.supervisor,
    wr.po_number,
    wr.invoice_number,
    wr.release_number,
    bl.name,
    wr.pmp_id,
    wr.status
FROM
    DGS_Archibus.afm.wrhwr wr
    LEFT OUTER JOIN DGS_Archibus.afm.bl bl ON wr.bl_id = bl.bl_id
ORDER BY
    wr.wr_id