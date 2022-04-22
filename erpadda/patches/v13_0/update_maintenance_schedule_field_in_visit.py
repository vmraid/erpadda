import vmraid


def execute():
	vmraid.reload_doctype("Maintenance Visit")
	vmraid.reload_doctype("Maintenance Visit Purpose")

	# Updates the Maintenance Schedule link to fetch serial nos
	from vmraid.query_builder.functions import Coalesce

	mvp = vmraid.qb.DocType("Maintenance Visit Purpose")
	mv = vmraid.qb.DocType("Maintenance Visit")

	vmraid.qb.update(mv).join(mvp).on(mvp.parent == mv.name).set(
		mv.maintenance_schedule, Coalesce(mvp.prevdoc_docname, "")
	).where(
		(mv.maintenance_type == "Scheduled") & (mvp.prevdoc_docname.notnull()) & (mv.docstatus < 2)
	).run(
		as_dict=1
	)
