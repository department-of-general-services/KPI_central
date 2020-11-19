SELECT
    wo.wo_id,
    wr.date_requested,
    wr.time_requested,
    wr.date_completed,
    wr.time_completed,
    wr.date_closed,
    wr.pmp_id,
    wr.bl_id,
    wo.cost_total,
    wo.cost_labor,
    wo.cost_parts,
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
    DGS_Archibus.afm.wohwo wo
    LEFT JOIN DGS_Archibus.afm.wrhwr wr ON wo.wo_id = wr.wo_id
    LEFT JOIN DGS_Archibus.afm.bl bl ON wo.bl_id = bl.bl_id
ORDER BY
    wo.wo_id