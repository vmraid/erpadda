import vmraid


def execute():
	vmraid.reload_doc("hr", "doctype", "employee_advance")

	advance = vmraid.qb.DocType("Employee Advance")
	(
		vmraid.qb.update(advance)
		.set(advance.status, "Returned")
		.where(
			(advance.docstatus == 1)
			& ((advance.return_amount) & (advance.paid_amount == advance.return_amount))
			& (advance.status == "Paid")
		)
	).run()

	(
		vmraid.qb.update(advance)
		.set(advance.status, "Partly Claimed and Returned")
		.where(
			(advance.docstatus == 1)
			& (
				(advance.claimed_amount & advance.return_amount)
				& (advance.paid_amount == (advance.return_amount + advance.claimed_amount))
			)
			& (advance.status == "Paid")
		)
	).run()
