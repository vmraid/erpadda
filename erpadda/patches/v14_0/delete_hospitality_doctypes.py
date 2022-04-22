import vmraid


def execute():
	modules = ["Hotels", "Restaurant"]

	for module in modules:
		vmraid.delete_doc("Module Def", module, ignore_missing=True, force=True)

		vmraid.delete_doc("Workspace", module, ignore_missing=True, force=True)

		reports = vmraid.get_all("Report", {"module": module, "is_standard": "Yes"}, pluck="name")
		for report in reports:
			vmraid.delete_doc("Report", report, ignore_missing=True, force=True)

		dashboards = vmraid.get_all("Dashboard", {"module": module, "is_standard": 1}, pluck="name")
		for dashboard in dashboards:
			vmraid.delete_doc("Dashboard", dashboard, ignore_missing=True, force=True)

		doctypes = vmraid.get_all("DocType", {"module": module, "custom": 0}, pluck="name")
		for doctype in doctypes:
			vmraid.delete_doc("DocType", doctype, ignore_missing=True)

	custom_fields = [
		{"dt": "Sales Invoice", "fieldname": "restaurant"},
		{"dt": "Sales Invoice", "fieldname": "restaurant_table"},
		{"dt": "Price List", "fieldname": "restaurant_menu"},
	]

	for field in custom_fields:
		custom_field = vmraid.db.get_value("Custom Field", field)
		vmraid.delete_doc("Custom Field", custom_field, ignore_missing=True)
