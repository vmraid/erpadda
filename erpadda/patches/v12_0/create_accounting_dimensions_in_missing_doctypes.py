import vmraid
from vmraid.custom.doctype.custom_field.custom_field import create_custom_field


def execute():

	vmraid.reload_doc("accounts", "doctype", "accounting_dimension")

	accounting_dimensions = vmraid.db.sql(
		"""select fieldname, label, document_type, disabled from
		`tabAccounting Dimension`""",
		as_dict=1,
	)

	if not accounting_dimensions:
		return

	count = 1
	for d in accounting_dimensions:

		if count % 2 == 0:
			insert_after_field = "dimension_col_break"
		else:
			insert_after_field = "accounting_dimensions_section"

		for doctype in [
			"Subscription Plan",
			"Subscription",
			"Opening Invoice Creation Tool",
			"Opening Invoice Creation Tool Item",
			"Expense Claim Detail",
			"Expense Taxes and Charges",
		]:

			field = vmraid.db.get_value("Custom Field", {"dt": doctype, "fieldname": d.fieldname})

			if field:
				continue

			df = {
				"fieldname": d.fieldname,
				"label": d.label,
				"fieldtype": "Link",
				"options": d.document_type,
				"insert_after": insert_after_field,
			}

			create_custom_field(doctype, df)
			vmraid.clear_cache(doctype=doctype)

		count += 1
