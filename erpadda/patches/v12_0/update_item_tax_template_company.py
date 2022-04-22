import vmraid


def execute():
	vmraid.reload_doc("accounts", "doctype", "item_tax_template")

	item_tax_template_list = vmraid.get_list("Item Tax Template")
	for template in item_tax_template_list:
		doc = vmraid.get_doc("Item Tax Template", template.name)
		for tax in doc.taxes:
			doc.company = vmraid.get_value("Account", tax.tax_type, "company")
			break
		doc.save()
