import vmraid


def execute():
	vmraid.reload_doc("HR", "doctype", "Leave Allocation")
	vmraid.reload_doc("HR", "doctype", "Leave Ledger Entry")
	vmraid.db.sql(
		"""update `tabLeave Ledger Entry` as lle set company = (select company from `tabEmployee` where employee = lle.employee)"""
	)
	vmraid.db.sql(
		"""update `tabLeave Allocation` as la set company = (select company from `tabEmployee` where employee = la.employee)"""
	)
