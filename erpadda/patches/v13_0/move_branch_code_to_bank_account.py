# Copyright (c) 2019, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid


def execute():

	vmraid.reload_doc("accounts", "doctype", "bank_account")
	vmraid.reload_doc("accounts", "doctype", "bank")

	if vmraid.db.has_column("Bank", "branch_code") and vmraid.db.has_column(
		"Bank Account", "branch_code"
	):
		vmraid.db.sql(
			"""UPDATE `tabBank` b, `tabBank Account` ba
			SET ba.branch_code = b.branch_code
			WHERE ba.bank = b.name AND
			ifnull(b.branch_code, '') != '' AND ifnull(ba.branch_code, '') = ''"""
		)
