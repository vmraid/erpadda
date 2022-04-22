import vmraid


def execute():
	# handle type casting for is_cancelled field
	module_doctypes = (
		("stock", "Stock Ledger Entry"),
		("stock", "Serial No"),
		("accounts", "GL Entry"),
	)

	for module, doctype in module_doctypes:
		if (
			not vmraid.db.has_column(doctype, "is_cancelled")
			or vmraid.db.get_column_type(doctype, "is_cancelled").lower() == "int(1)"
		):
			continue

		vmraid.db.sql(
			"""
				UPDATE `tab{doctype}`
				SET is_cancelled = 0
				where is_cancelled in ('', 'No') or is_cancelled is NULL""".format(
				doctype=doctype
			)
		)
		vmraid.db.sql(
			"""
				UPDATE `tab{doctype}`
				SET is_cancelled = 1
				where is_cancelled = 'Yes'""".format(
				doctype=doctype
			)
		)

		vmraid.reload_doc(module, "doctype", vmraid.scrub(doctype))
