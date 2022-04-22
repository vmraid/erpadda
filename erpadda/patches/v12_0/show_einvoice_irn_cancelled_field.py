from __future__ import unicode_literals

import vmraid


def execute():
	company = vmraid.get_all("Company", filters={"country": "India"})
	if not company:
		return

	irn_cancelled_field = vmraid.db.exists(
		"Custom Field", {"dt": "Sales Invoice", "fieldname": "irn_cancelled"}
	)
	if irn_cancelled_field:
		vmraid.db.set_value("Custom Field", irn_cancelled_field, "depends_on", "eval: doc.irn")
		vmraid.db.set_value("Custom Field", irn_cancelled_field, "read_only", 0)
