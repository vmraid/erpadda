import vmraid


def execute():
	company = vmraid.db.get_single_value("Global Defaults", "default_company")
	doctypes = [
		"Clinical Procedure",
		"Inpatient Record",
		"Lab Test",
		"Sample Collection",
		"Patient Appointment",
		"Patient Encounter",
		"Vital Signs",
		"Therapy Session",
		"Therapy Plan",
		"Patient Assessment",
	]
	for entry in doctypes:
		if vmraid.db.exists("DocType", entry):
			vmraid.reload_doc("Healthcare", "doctype", entry)
			vmraid.db.sql(
				"update `tab{dt}` set company = {company} where ifnull(company, '') = ''".format(
					dt=entry, company=vmraid.db.escape(company)
				)
			)
