import vmraid


def execute():
	vmraid.reload_doc("hr", "doctype", "expense_claim_detail")
	vmraid.db.sql(
		"""
		UPDATE `tabExpense Claim Detail` child, `tabExpense Claim` par
		SET child.cost_center = par.cost_center
		WHERE child.parent = par.name
	"""
	)
