import vmraid


def execute():
	vmraid.reload_doc("accounts", "doctype", "tax_category")
	vmraid.reload_doc("stock", "doctype", "item_manufacturer")
	company = vmraid.get_all("Company", filters={"country": "India"})
	if not company:
		return
	if vmraid.db.exists("Custom Field", "Company-bank_remittance_section"):
		deprecated_fields = [
			"bank_remittance_section",
			"client_code",
			"remittance_column_break",
			"product_code",
		]
		for i in range(len(deprecated_fields)):
			vmraid.delete_doc("Custom Field", "Company-" + deprecated_fields[i])
