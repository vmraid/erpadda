# License: GNU General Public License v3. See license.txt


import vmraid


def execute():
	if vmraid.db.table_exists("POS Closing Voucher"):
		if not vmraid.db.exists("DocType", "POS Closing Entry"):
			vmraid.rename_doc("DocType", "POS Closing Voucher", "POS Closing Entry", force=True)

		if not vmraid.db.exists("DocType", "POS Closing Entry Taxes"):
			vmraid.rename_doc("DocType", "POS Closing Voucher Taxes", "POS Closing Entry Taxes", force=True)

		if not vmraid.db.exists("DocType", "POS Closing Voucher Details"):
			vmraid.rename_doc(
				"DocType", "POS Closing Voucher Details", "POS Closing Entry Detail", force=True
			)

		vmraid.reload_doc("Accounts", "doctype", "POS Closing Entry")
		vmraid.reload_doc("Accounts", "doctype", "POS Closing Entry Taxes")
		vmraid.reload_doc("Accounts", "doctype", "POS Closing Entry Detail")

	if vmraid.db.exists("DocType", "POS Closing Voucher"):
		vmraid.delete_doc("DocType", "POS Closing Voucher")
		vmraid.delete_doc("DocType", "POS Closing Voucher Taxes")
		vmraid.delete_doc("DocType", "POS Closing Voucher Details")
		vmraid.delete_doc("DocType", "POS Closing Voucher Invoices")
