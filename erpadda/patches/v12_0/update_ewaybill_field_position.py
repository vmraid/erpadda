import vmraid


def execute():
	company = vmraid.get_all("Company", filters={"country": "India"})

	if not company:
		return

	field = vmraid.db.get_value("Custom Field", {"dt": "Sales Invoice", "fieldname": "ewaybill"})

	if field:
		ewaybill_field = vmraid.get_doc("Custom Field", field)

		ewaybill_field.flags.ignore_validate = True

		ewaybill_field.update(
			{
				"fieldname": "ewaybill",
				"label": "e-Way Bill No.",
				"fieldtype": "Data",
				"depends_on": "eval:(doc.docstatus === 1)",
				"allow_on_submit": 1,
				"insert_after": "tax_id",
				"translatable": 0,
			}
		)

		ewaybill_field.save()
