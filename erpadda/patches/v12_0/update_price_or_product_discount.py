import vmraid


def execute():
	vmraid.reload_doc("accounts", "doctype", "pricing_rule")

	vmraid.db.sql(
		""" UPDATE `tabPricing Rule` SET price_or_product_discount = 'Price'
		WHERE ifnull(price_or_product_discount,'') = '' """
	)
