import vmraid


def execute():
	if vmraid.db.has_table("Tax Withholding Category") and vmraid.db.has_column(
		"Tax Withholding Category", "round_off_tax_amount"
	):
		vmraid.db.sql(
			"""
			UPDATE `tabTax Withholding Category` set round_off_tax_amount = 0
			WHERE round_off_tax_amount IS NULL
		"""
		)
