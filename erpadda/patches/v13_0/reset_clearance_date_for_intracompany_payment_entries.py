# Copyright (c) 2019, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid


def execute():
	"""
	Reset Clearance Date for Payment Entries of type Internal Transfer that have only been reconciled with one Bank Transaction.
	This will allow the Payment Entries to be reconciled with the second Bank Transaction using the Bank Reconciliation Tool.
	"""

	intra_company_pe = get_intra_company_payment_entries_with_clearance_dates()
	reconciled_bank_transactions = get_reconciled_bank_transactions(intra_company_pe)

	for payment_entry in reconciled_bank_transactions:
		if len(reconciled_bank_transactions[payment_entry]) == 1:
			vmraid.db.set_value("Payment Entry", payment_entry, "clearance_date", None)


def get_intra_company_payment_entries_with_clearance_dates():
	return vmraid.get_all(
		"Payment Entry",
		filters={"payment_type": "Internal Transfer", "clearance_date": ["not in", None]},
		pluck="name",
	)


def get_reconciled_bank_transactions(intra_company_pe):
	"""Returns dictionary where each key:value pair is Payment Entry : List of Bank Transactions reconciled with Payment Entry"""

	reconciled_bank_transactions = {}

	for payment_entry in intra_company_pe:
		reconciled_bank_transactions[payment_entry] = vmraid.get_all(
			"Bank Transaction Payments", filters={"payment_entry": payment_entry}, pluck="parent"
		)

	return reconciled_bank_transactions
