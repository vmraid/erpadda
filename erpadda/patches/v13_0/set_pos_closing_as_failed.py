import vmraid


def execute():
	vmraid.reload_doc("accounts", "doctype", "pos_closing_entry")

	vmraid.db.sql("update `tabPOS Closing Entry` set `status` = 'Failed' where `status` = 'Queued'")
