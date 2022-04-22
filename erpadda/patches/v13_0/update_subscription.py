# Copyright (c) 2019, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid


def execute():

	vmraid.reload_doc("accounts", "doctype", "subscription")
	vmraid.reload_doc("accounts", "doctype", "subscription_invoice")
	vmraid.reload_doc("accounts", "doctype", "subscription_plan")

	if vmraid.db.has_column("Subscription", "customer"):
		vmraid.db.sql(
			"""
			UPDATE `tabSubscription`
			SET
				start_date = start,
				party_type = 'Customer',
				party = customer,
				sales_tax_template = tax_template
			WHERE IFNULL(party,'') = ''
		"""
		)

	vmraid.db.sql(
		"""
		UPDATE `tabSubscription Invoice`
		SET document_type = 'Sales Invoice'
		WHERE IFNULL(document_type, '') = ''
	"""
	)

	price_determination_map = {
		"Fixed rate": "Fixed Rate",
		"Based on price list": "Based On Price List",
	}

	for key, value in price_determination_map.items():
		vmraid.db.sql(
			"""
			UPDATE `tabSubscription Plan`
			SET price_determination = %s
			WHERE price_determination = %s
		""",
			(value, key),
		)
