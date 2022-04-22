import vmraid


def execute():
	vmraid.reload_doctype("Pricing Rule")

	currency = vmraid.db.get_default("currency")
	for doc in vmraid.get_all("Pricing Rule", fields=["company", "name"]):
		if doc.company:
			currency = vmraid.get_cached_value("Company", doc.company, "default_currency")

		vmraid.db.sql(
			"""update `tabPricing Rule` set currency = %s where name = %s""", (currency, doc.name)
		)
