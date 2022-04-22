import vmraid


def execute():
	vmraid.reload_doc("accounts", "doctype", "bank", force=1)

	if (
		vmraid.db.table_exists("Bank")
		and vmraid.db.table_exists("Bank Account")
		and vmraid.db.has_column("Bank Account", "swift_number")
	):
		try:
			vmraid.db.sql(
				"""
				UPDATE `tabBank` b, `tabBank Account` ba
				SET b.swift_number = ba.swift_number WHERE b.name = ba.bank
			"""
			)
		except Exception as e:
			vmraid.log_error(e, title="Patch Migration Failed")

	vmraid.reload_doc("accounts", "doctype", "bank_account")
	vmraid.reload_doc("accounts", "doctype", "payment_request")
