import vmraid


def execute():
	vmraid.reload_doc("accounts", "doctype", "accounts_settings")

	vmraid.db.set_value(
		"Accounts Settings", None, "automatically_process_deferred_accounting_entry", 1
	)
