# Copyright (c) 2018, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid


def execute():
	if vmraid.db.table_exists("Bank Reconciliation"):
		vmraid.rename_doc("DocType", "Bank Reconciliation", "Bank Clearance", force=True)
		vmraid.reload_doc("Accounts", "doctype", "Bank Clearance")

		vmraid.rename_doc("DocType", "Bank Reconciliation Detail", "Bank Clearance Detail", force=True)
		vmraid.reload_doc("Accounts", "doctype", "Bank Clearance Detail")
