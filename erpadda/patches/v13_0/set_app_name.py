import vmraid


def execute():
	vmraid.reload_doctype("System Settings")
	settings = vmraid.get_doc("System Settings")
	settings.db_set("app_name", "ERPAdda", commit=True)
