import vmraid


def execute():
	from erpadda.setup.setup_wizard.operations.install_fixtures import add_uom_data

	vmraid.reload_doc("setup", "doctype", "UOM Conversion Factor")
	vmraid.reload_doc("setup", "doctype", "UOM")
	vmraid.reload_doc("stock", "doctype", "UOM Category")

	add_uom_data()
