import vmraid


def execute():
	vmraid.reload_doc("hr", "doctype", "hr_settings")
	vmraid.db.set_value("HR Settings", None, "payroll_based_on", "Leave")
