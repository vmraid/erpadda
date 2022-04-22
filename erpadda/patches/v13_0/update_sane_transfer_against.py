import vmraid


def execute():
	bom = vmraid.qb.DocType("BOM")

	(
		vmraid.qb.update(bom)
		.set(bom.transfer_material_against, "Work Order")
		.where(bom.with_operations == 0)
	).run()
