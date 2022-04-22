import vmraid


def execute():
	company = vmraid.get_all("Company", filters={"country": "India"})
	if not company:
		return

	# Update custom fields
	fieldname = vmraid.db.get_value("Custom Field", {"dt": "Customer", "fieldname": "export_type"})
	if fieldname:
		vmraid.db.set_value(
			"Custom Field",
			fieldname,
			{
				"default": "",
				"mandatory_depends_on": 'eval:in_list(["SEZ", "Overseas", "Deemed Export"], doc.gst_category)',
			},
		)

	fieldname = vmraid.db.get_value("Custom Field", {"dt": "Supplier", "fieldname": "export_type"})
	if fieldname:
		vmraid.db.set_value(
			"Custom Field",
			fieldname,
			{"default": "", "mandatory_depends_on": 'eval:in_list(["SEZ", "Overseas"], doc.gst_category)'},
		)

	# Update Customer/Supplier Masters
	vmraid.db.sql(
		"""
		UPDATE `tabCustomer` set export_type = '' WHERE gst_category NOT IN ('SEZ', 'Overseas', 'Deemed Export')
	"""
	)

	vmraid.db.sql(
		"""
		UPDATE `tabSupplier` set export_type = '' WHERE gst_category NOT IN ('SEZ', 'Overseas')
	"""
	)
