from __future__ import unicode_literals

import vmraid


def execute():
	company = vmraid.get_all("Company", filters={"country": "India"})
	if not company or not vmraid.db.count("E Invoice User"):
		return

	vmraid.reload_doc("regional", "doctype", "e_invoice_user")
	for creds in vmraid.db.get_all("E Invoice User", fields=["name", "gstin"]):
		company_name = vmraid.db.sql(
			"""
			select dl.link_name from `tabAddress` a, `tabDynamic Link` dl
			where a.gstin = %s and dl.parent = a.name and dl.link_doctype = 'Company'
		""",
			(creds.get("gstin")),
		)
		if company_name and len(company_name) > 0:
			vmraid.db.set_value("E Invoice User", creds.get("name"), "company", company_name[0][0])
