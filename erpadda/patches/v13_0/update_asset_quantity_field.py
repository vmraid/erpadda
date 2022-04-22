import vmraid


def execute():
	if vmraid.db.count("Asset"):
		vmraid.reload_doc("assets", "doctype", "Asset")
		asset = vmraid.qb.DocType("Asset")
		vmraid.qb.update(asset).set(asset.asset_quantity, 1).run()
