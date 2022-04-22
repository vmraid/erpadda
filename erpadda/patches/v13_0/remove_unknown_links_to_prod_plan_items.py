import vmraid


def execute():
	"""
	Remove "production_plan_item" field where linked field doesn't exist in tha table.
	"""

	work_order = vmraid.qb.DocType("Work Order")
	pp_item = vmraid.qb.DocType("Production Plan Item")

	broken_work_orders = (
		vmraid.qb.from_(work_order)
		.left_join(pp_item)
		.on(work_order.production_plan_item == pp_item.name)
		.select(work_order.name)
		.where(
			(work_order.docstatus == 0)
			& (work_order.production_plan_item.notnull())
			& (work_order.production_plan_item.like("new-production-plan%"))
			& (pp_item.name.isnull())
		)
	).run(pluck=True)

	if not broken_work_orders:
		return

	(
		vmraid.qb.update(work_order)
		.set(work_order.production_plan_item, None)
		.where(work_order.name.isin(broken_work_orders))
	).run()
