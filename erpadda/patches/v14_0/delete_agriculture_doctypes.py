import vmraid


def execute():
	vmraid.delete_doc("Module Def", "Agriculture", ignore_missing=True, force=True)

	vmraid.delete_doc("Workspace", "Agriculture", ignore_missing=True, force=True)

	reports = vmraid.get_all("Report", {"module": "agriculture", "is_standard": "Yes"}, pluck="name")
	for report in reports:
		vmraid.delete_doc("Report", report, ignore_missing=True, force=True)

	dashboards = vmraid.get_all(
		"Dashboard", {"module": "agriculture", "is_standard": 1}, pluck="name"
	)
	for dashboard in dashboards:
		vmraid.delete_doc("Dashboard", dashboard, ignore_missing=True, force=True)

	doctypes = vmraid.get_all("DocType", {"module": "agriculture", "custom": 0}, pluck="name")
	for doctype in doctypes:
		vmraid.delete_doc("DocType", doctype, ignore_missing=True)
