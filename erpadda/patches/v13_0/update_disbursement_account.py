import vmraid


def execute():

	vmraid.reload_doc("loan_management", "doctype", "loan_type")
	vmraid.reload_doc("loan_management", "doctype", "loan")

	loan_type = vmraid.qb.DocType("Loan Type")
	loan = vmraid.qb.DocType("Loan")

	vmraid.qb.update(loan_type).set(loan_type.disbursement_account, loan_type.payment_account).run()

	vmraid.qb.update(loan).set(loan.disbursement_account, loan.payment_account).run()
