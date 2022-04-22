# Copyright (c) 2015, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid


def execute():
	vmraid.reload_doc("accounts", "doctype", "bank_transaction")

	bank_transaction_fields = vmraid.get_meta("Bank Transaction").get_valid_columns()

	if "debit" in bank_transaction_fields:
		vmraid.db.sql(
			""" UPDATE `tabBank Transaction`
            SET status = 'Reconciled'
            WHERE
                status = 'Settled' and (debit = allocated_amount or credit = allocated_amount)
                and ifnull(allocated_amount, 0) > 0
        """
		)

	elif "deposit" in bank_transaction_fields:
		vmraid.db.sql(
			""" UPDATE `tabBank Transaction`
            SET status = 'Reconciled'
            WHERE
                status = 'Settled' and (deposit = allocated_amount or withdrawal = allocated_amount)
                and ifnull(allocated_amount, 0) > 0
        """
		)
