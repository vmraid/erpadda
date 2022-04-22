import vmraid

from erpadda.regional.india.setup import make_custom_fields


def execute():
	company = vmraid.get_all("Company", filters={"country": "India"})
	if not company:
		return

	vmraid.reload_doc("Payroll", "doctype", "payroll_period")
	vmraid.reload_doc("Payroll", "doctype", "employee_tax_exemption_declaration")
	vmraid.reload_doc("Payroll", "doctype", "employee_tax_exemption_proof_submission")
	vmraid.reload_doc("Payroll", "doctype", "employee_tax_exemption_declaration_category")
	vmraid.reload_doc("Payroll", "doctype", "employee_tax_exemption_proof_submission_detail")

	vmraid.reload_doc("accounts", "doctype", "tax_category")

	for doctype in ["Sales Invoice", "Delivery Note", "Purchase Invoice"]:
		vmraid.db.sql(
			"""delete from `tabCustom Field` where dt = %s
			and fieldname in ('port_code', 'shipping_bill_number', 'shipping_bill_date')""",
			doctype,
		)

	make_custom_fields()

	vmraid.db.sql(
		"""
		update `tabCustom Field`
		set reqd = 0, `default` = ''
		where fieldname = 'reason_for_issuing_document'
	"""
	)

	vmraid.db.sql(
		"""
		update tabAddress
		set gst_state_number=concat("0", gst_state_number)
		where ifnull(gst_state_number, '') != '' and gst_state_number<10
	"""
	)
