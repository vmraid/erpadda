import vmraid


def execute():
	vmraid.reload_doc("loan_management", "doctype", "loan")
	loan = vmraid.qb.DocType("Loan")

	for company in vmraid.get_all("Company", pluck="name"):
		default_cost_center = vmraid.db.get_value("Company", company, "cost_center")
		vmraid.qb.update(loan).set(loan.cost_center, default_cost_center).where(
			loan.company == company
		).run()
