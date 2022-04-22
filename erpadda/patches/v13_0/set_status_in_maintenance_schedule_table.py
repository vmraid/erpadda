import vmraid


def execute():
	vmraid.reload_doc("maintenance", "doctype", "Maintenance Schedule Detail")
	vmraid.db.sql(
		"""
		UPDATE `tabMaintenance Schedule Detail`
		SET completion_status = 'Pending'
		WHERE docstatus < 2
	"""
	)
