import vmraid


def execute():
	vmraid.reload_doc("crm", "doctype", "lead")
	vmraid.db.sql(
		"""
		UPDATE
			`tabLead`
		SET
			title = IF(organization_lead = 1, company_name, lead_name)
	"""
	)
