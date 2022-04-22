import vmraid


def execute():
	vmraid.reload_doctype("Payment Entry")
	vmraid.db.sql(
		"""update `tabPayment Entry` set status = CASE
		WHEN docstatus = 1 THEN 'Submitted'
		WHEN docstatus = 2 THEN 'Cancelled'
		ELSE 'Draft'
		END;"""
	)
