import vmraid


def execute():
	from erpadda.setup.setup_wizard.operations.install_fixtures import add_uom_data

	vmraid.reload_doc("setup", "doctype", "UOM Conversion Factor")
	vmraid.reload_doc("setup", "doctype", "UOM")
	vmraid.reload_doc("stock", "doctype", "UOM Category")

	if not vmraid.db.a_row_exists("UOM Conversion Factor"):
		add_uom_data()
	else:
		# delete conversion data and insert again
		vmraid.db.sql("delete from `tabUOM Conversion Factor`")
		try:
			vmraid.delete_doc("UOM", "Hundredweight")
			vmraid.delete_doc("UOM", "Pound Cubic Yard")
		except vmraid.LinkExistsError:
			pass

		add_uom_data()
