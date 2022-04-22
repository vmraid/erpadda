import vmraid


def execute():
	vmraid.reload_doc("setup", "doctype", "uom")

	uom = vmraid.qb.DocType("UOM")

	(
		vmraid.qb.update(uom)
		.set(uom.enabled, 1)
		.where(uom.creation >= "2021-10-18")  # date when this field was released
	).run()
