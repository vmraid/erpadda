# Copyright (c) 2019, VMRaid and contributors
# For license information, please see license.txt


from functools import reduce

import vmraid
from vmraid.utils import flt

from erpadda.controllers.status_updater import StatusUpdater


class BankTransaction(StatusUpdater):
	def after_insert(self):
		self.unallocated_amount = abs(flt(self.withdrawal) - flt(self.deposit))

	def on_submit(self):
		self.clear_linked_payment_entries()
		self.set_status()

	def on_update_after_submit(self):
		self.update_allocations()
		self.clear_linked_payment_entries()
		self.set_status(update=True)

	def on_cancel(self):
		self.clear_linked_payment_entries(for_cancel=True)
		self.set_status(update=True)

	def update_allocations(self):
		if self.payment_entries:
			allocated_amount = reduce(
				lambda x, y: flt(x) + flt(y), [x.allocated_amount for x in self.payment_entries]
			)
		else:
			allocated_amount = 0

		if allocated_amount:
			vmraid.db.set_value(self.doctype, self.name, "allocated_amount", flt(allocated_amount))
			vmraid.db.set_value(
				self.doctype,
				self.name,
				"unallocated_amount",
				abs(flt(self.withdrawal) - flt(self.deposit)) - flt(allocated_amount),
			)

		else:
			vmraid.db.set_value(self.doctype, self.name, "allocated_amount", 0)
			vmraid.db.set_value(
				self.doctype, self.name, "unallocated_amount", abs(flt(self.withdrawal) - flt(self.deposit))
			)

		amount = self.deposit or self.withdrawal
		if amount == self.allocated_amount:
			vmraid.db.set_value(self.doctype, self.name, "status", "Reconciled")

		self.reload()

	def clear_linked_payment_entries(self, for_cancel=False):
		for payment_entry in self.payment_entries:
			if payment_entry.payment_document in [
				"Payment Entry",
				"Journal Entry",
				"Purchase Invoice",
				"Expense Claim",
				"Loan Repayment",
				"Loan Disbursement",
			]:
				self.clear_simple_entry(payment_entry, for_cancel=for_cancel)

			elif payment_entry.payment_document == "Sales Invoice":
				self.clear_sales_invoice(payment_entry, for_cancel=for_cancel)

	def clear_simple_entry(self, payment_entry, for_cancel=False):
		if payment_entry.payment_document == "Payment Entry":
			if (
				vmraid.db.get_value("Payment Entry", payment_entry.payment_entry, "payment_type")
				== "Internal Transfer"
			):
				if len(get_reconciled_bank_transactions(payment_entry)) < 2:
					return

		clearance_date = self.date if not for_cancel else None
		vmraid.db.set_value(
			payment_entry.payment_document, payment_entry.payment_entry, "clearance_date", clearance_date
		)

	def clear_sales_invoice(self, payment_entry, for_cancel=False):
		clearance_date = self.date if not for_cancel else None
		vmraid.db.set_value(
			"Sales Invoice Payment",
			dict(parenttype=payment_entry.payment_document, parent=payment_entry.payment_entry),
			"clearance_date",
			clearance_date,
		)


def get_reconciled_bank_transactions(payment_entry):
	reconciled_bank_transactions = vmraid.get_all(
		"Bank Transaction Payments",
		filters={"payment_entry": payment_entry.payment_entry},
		fields=["parent"],
	)

	return reconciled_bank_transactions


def get_total_allocated_amount(payment_entry):
	return vmraid.db.sql(
		"""
		SELECT
			SUM(btp.allocated_amount) as allocated_amount,
			bt.name
		FROM
			`tabBank Transaction Payments` as btp
		LEFT JOIN
			`tabBank Transaction` bt ON bt.name=btp.parent
		WHERE
			btp.payment_document = %s
		AND
			btp.payment_entry = %s
		AND
			bt.docstatus = 1""",
		(payment_entry.payment_document, payment_entry.payment_entry),
		as_dict=True,
	)


def get_paid_amount(payment_entry, currency, bank_account):
	if payment_entry.payment_document in ["Payment Entry", "Sales Invoice", "Purchase Invoice"]:

		paid_amount_field = "paid_amount"
		if payment_entry.payment_document == "Payment Entry":
			doc = vmraid.get_doc("Payment Entry", payment_entry.payment_entry)

			if doc.payment_type == "Receive":
				paid_amount_field = (
					"received_amount" if doc.paid_to_account_currency == currency else "base_received_amount"
				)
			elif doc.payment_type == "Pay":
				paid_amount_field = (
					"paid_amount" if doc.paid_to_account_currency == currency else "base_paid_amount"
				)

		return vmraid.db.get_value(
			payment_entry.payment_document, payment_entry.payment_entry, paid_amount_field
		)

	elif payment_entry.payment_document == "Journal Entry":
		return vmraid.db.get_value(
			"Journal Entry Account",
			{"parent": payment_entry.payment_entry, "account": bank_account},
			"sum(credit_in_account_currency)",
		)

	elif payment_entry.payment_document == "Expense Claim":
		return vmraid.db.get_value(
			payment_entry.payment_document, payment_entry.payment_entry, "total_amount_reimbursed"
		)

	elif payment_entry.payment_document == "Loan Disbursement":
		return vmraid.db.get_value(
			payment_entry.payment_document, payment_entry.payment_entry, "disbursed_amount"
		)

	elif payment_entry.payment_document == "Loan Repayment":
		return vmraid.db.get_value(
			payment_entry.payment_document, payment_entry.payment_entry, "amount_paid"
		)

	else:
		vmraid.throw(
			"Please reconcile {0}: {1} manually".format(
				payment_entry.payment_document, payment_entry.payment_entry
			)
		)


@vmraid.whitelist()
def unclear_reference_payment(doctype, docname):
	if vmraid.db.exists(doctype, docname):
		doc = vmraid.get_doc(doctype, docname)
		if doctype == "Sales Invoice":
			vmraid.db.set_value(
				"Sales Invoice Payment",
				dict(parenttype=doc.payment_document, parent=doc.payment_entry),
				"clearance_date",
				None,
			)
		else:
			vmraid.db.set_value(doc.payment_document, doc.payment_entry, "clearance_date", None)

		return doc.payment_entry
