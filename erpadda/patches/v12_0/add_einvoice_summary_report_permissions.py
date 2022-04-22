from __future__ import unicode_literals

import vmraid


def execute():
	company = vmraid.get_all("Company", filters={"country": "India"})
	if not company:
		return

	if vmraid.db.exists("Report", "E-Invoice Summary") and not vmraid.db.get_value(
		"Custom Role", dict(report="E-Invoice Summary")
	):
		vmraid.get_doc(
			dict(
				doctype="Custom Role",
				report="E-Invoice Summary",
				roles=[dict(role="Accounts User"), dict(role="Accounts Manager")],
			)
		).insert()
