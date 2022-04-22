# Copyright (c) 2018, VMRaid and Contributors
# See license.txt

import json
import unittest

import vmraid

from erpadda.accounts.doctype.bank_reconciliation_tool.bank_reconciliation_tool import (
	get_linked_payments,
	reconcile_vouchers,
)
from erpadda.accounts.doctype.payment_entry.test_payment_entry import get_payment_entry
from erpadda.accounts.doctype.pos_profile.test_pos_profile import make_pos_profile
from erpadda.accounts.doctype.purchase_invoice.test_purchase_invoice import make_purchase_invoice
from erpadda.accounts.doctype.sales_invoice.test_sales_invoice import create_sales_invoice

test_dependencies = ["Item", "Cost Center"]


class TestBankTransaction(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		make_pos_profile()
		add_transactions()
		add_vouchers()

	@classmethod
	def tearDownClass(cls):
		for bt in vmraid.get_all("Bank Transaction"):
			doc = vmraid.get_doc("Bank Transaction", bt.name)
			if doc.docstatus == 1:
				doc.cancel()
			doc.delete()

		# Delete directly in DB to avoid validation errors for countries not allowing deletion
		vmraid.db.sql("""delete from `tabPayment Entry Reference`""")
		vmraid.db.sql("""delete from `tabPayment Entry`""")

		# Delete POS Profile
		vmraid.db.sql("delete from `tabPOS Profile`")

	# This test checks if ERPAdda is able to provide a linked payment for a bank transaction based on the amount of the bank transaction.
	def test_linked_payments(self):
		bank_transaction = vmraid.get_doc(
			"Bank Transaction",
			dict(description="Re 95282925234 FE/000002917 AT171513000281183046 Conrad Electronic"),
		)
		linked_payments = get_linked_payments(bank_transaction.name, ["payment_entry", "exact_match"])
		self.assertTrue(linked_payments[0][6] == "Conrad Electronic")

	# This test validates a simple reconciliation leading to the clearance of the bank transaction and the payment
	def test_reconcile(self):
		bank_transaction = vmraid.get_doc(
			"Bank Transaction",
			dict(description="1512567 BG/000003025 OPSKATTUZWXXX AT776000000098709849 Herr G"),
		)
		payment = vmraid.get_doc("Payment Entry", dict(party="Mr G", paid_amount=1700))
		vouchers = json.dumps(
			[
				{
					"payment_doctype": "Payment Entry",
					"payment_name": payment.name,
					"amount": bank_transaction.unallocated_amount,
				}
			]
		)
		reconcile_vouchers(bank_transaction.name, vouchers)

		unallocated_amount = vmraid.db.get_value(
			"Bank Transaction", bank_transaction.name, "unallocated_amount"
		)
		self.assertTrue(unallocated_amount == 0)

		clearance_date = vmraid.db.get_value("Payment Entry", payment.name, "clearance_date")
		self.assertTrue(clearance_date is not None)

		bank_transaction.reload()
		bank_transaction.cancel()

		clearance_date = vmraid.db.get_value("Payment Entry", payment.name, "clearance_date")
		self.assertFalse(clearance_date)

	# Check if ERPAdda can correctly filter a linked payments based on the debit/credit amount
	def test_debit_credit_output(self):
		bank_transaction = vmraid.get_doc(
			"Bank Transaction",
			dict(description="Auszahlung Karte MC/000002916 AUTOMAT 698769 K002 27.10. 14:07"),
		)
		linked_payments = get_linked_payments(bank_transaction.name, ["payment_entry", "exact_match"])
		self.assertTrue(linked_payments[0][3])

	# Check error if already reconciled
	def test_already_reconciled(self):
		bank_transaction = vmraid.get_doc(
			"Bank Transaction",
			dict(description="1512567 BG/000002918 OPSKATTUZWXXX AT776000000098709837 Herr G"),
		)
		payment = vmraid.get_doc("Payment Entry", dict(party="Mr G", paid_amount=1200))
		vouchers = json.dumps(
			[
				{
					"payment_doctype": "Payment Entry",
					"payment_name": payment.name,
					"amount": bank_transaction.unallocated_amount,
				}
			]
		)
		reconcile_vouchers(bank_transaction.name, vouchers)

		bank_transaction = vmraid.get_doc(
			"Bank Transaction",
			dict(description="1512567 BG/000002918 OPSKATTUZWXXX AT776000000098709837 Herr G"),
		)
		payment = vmraid.get_doc("Payment Entry", dict(party="Mr G", paid_amount=1200))
		vouchers = json.dumps(
			[
				{
					"payment_doctype": "Payment Entry",
					"payment_name": payment.name,
					"amount": bank_transaction.unallocated_amount,
				}
			]
		)
		self.assertRaises(
			vmraid.ValidationError,
			reconcile_vouchers,
			bank_transaction_name=bank_transaction.name,
			vouchers=vouchers,
		)

	# Raise an error if debitor transaction vs debitor payment
	def test_clear_sales_invoice(self):
		bank_transaction = vmraid.get_doc(
			"Bank Transaction",
			dict(description="I2015000011 VD/000002514 ATWWXXX AT4701345000003510057 Bio"),
		)
		payment = vmraid.get_doc("Sales Invoice", dict(customer="Fayva", status=["=", "Paid"]))
		vouchers = json.dumps(
			[
				{
					"payment_doctype": "Sales Invoice",
					"payment_name": payment.name,
					"amount": bank_transaction.unallocated_amount,
				}
			]
		)
		reconcile_vouchers(bank_transaction.name, vouchers=vouchers)

		self.assertEqual(
			vmraid.db.get_value("Bank Transaction", bank_transaction.name, "unallocated_amount"), 0
		)
		self.assertTrue(
			vmraid.db.get_value("Sales Invoice Payment", dict(parent=payment.name), "clearance_date")
			is not None
		)


def create_bank_account(bank_name="Citi Bank", account_name="_Test Bank - _TC"):
	try:
		vmraid.get_doc(
			{
				"doctype": "Bank",
				"bank_name": bank_name,
			}
		).insert(ignore_if_duplicate=True)
	except vmraid.DuplicateEntryError:
		pass

	try:
		vmraid.get_doc(
			{
				"doctype": "Bank Account",
				"account_name": "Checking Account",
				"bank": bank_name,
				"account": account_name,
			}
		).insert(ignore_if_duplicate=True)
	except vmraid.DuplicateEntryError:
		pass


def add_transactions():
	create_bank_account()

	doc = vmraid.get_doc(
		{
			"doctype": "Bank Transaction",
			"description": "1512567 BG/000002918 OPSKATTUZWXXX AT776000000098709837 Herr G",
			"date": "2018-10-23",
			"deposit": 1200,
			"currency": "INR",
			"bank_account": "Checking Account - Citi Bank",
		}
	).insert()
	doc.submit()

	doc = vmraid.get_doc(
		{
			"doctype": "Bank Transaction",
			"description": "1512567 BG/000003025 OPSKATTUZWXXX AT776000000098709849 Herr G",
			"date": "2018-10-23",
			"deposit": 1700,
			"currency": "INR",
			"bank_account": "Checking Account - Citi Bank",
		}
	).insert()
	doc.submit()

	doc = vmraid.get_doc(
		{
			"doctype": "Bank Transaction",
			"description": "Re 95282925234 FE/000002917 AT171513000281183046 Conrad Electronic",
			"date": "2018-10-26",
			"withdrawal": 690,
			"currency": "INR",
			"bank_account": "Checking Account - Citi Bank",
		}
	).insert()
	doc.submit()

	doc = vmraid.get_doc(
		{
			"doctype": "Bank Transaction",
			"description": "Auszahlung Karte MC/000002916 AUTOMAT 698769 K002 27.10. 14:07",
			"date": "2018-10-27",
			"deposit": 3900,
			"currency": "INR",
			"bank_account": "Checking Account - Citi Bank",
		}
	).insert()
	doc.submit()

	doc = vmraid.get_doc(
		{
			"doctype": "Bank Transaction",
			"description": "I2015000011 VD/000002514 ATWWXXX AT4701345000003510057 Bio",
			"date": "2018-10-27",
			"withdrawal": 109080,
			"currency": "INR",
			"bank_account": "Checking Account - Citi Bank",
		}
	).insert()
	doc.submit()


def add_vouchers():
	try:
		vmraid.get_doc(
			{
				"doctype": "Supplier",
				"supplier_group": "All Supplier Groups",
				"supplier_type": "Company",
				"supplier_name": "Conrad Electronic",
			}
		).insert(ignore_if_duplicate=True)

	except vmraid.DuplicateEntryError:
		pass

	pi = make_purchase_invoice(supplier="Conrad Electronic", qty=1, rate=690)

	pe = get_payment_entry("Purchase Invoice", pi.name, bank_account="_Test Bank - _TC")
	pe.reference_no = "Conrad Oct 18"
	pe.reference_date = "2018-10-24"
	pe.insert()
	pe.submit()

	try:
		vmraid.get_doc(
			{
				"doctype": "Supplier",
				"supplier_group": "All Supplier Groups",
				"supplier_type": "Company",
				"supplier_name": "Mr G",
			}
		).insert(ignore_if_duplicate=True)
	except vmraid.DuplicateEntryError:
		pass

	pi = make_purchase_invoice(supplier="Mr G", qty=1, rate=1200)
	pe = get_payment_entry("Purchase Invoice", pi.name, bank_account="_Test Bank - _TC")
	pe.reference_no = "Herr G Oct 18"
	pe.reference_date = "2018-10-24"
	pe.insert()
	pe.submit()

	pi = make_purchase_invoice(supplier="Mr G", qty=1, rate=1700)
	pe = get_payment_entry("Purchase Invoice", pi.name, bank_account="_Test Bank - _TC")
	pe.reference_no = "Herr G Nov 18"
	pe.reference_date = "2018-11-01"
	pe.insert()
	pe.submit()

	try:
		vmraid.get_doc(
			{
				"doctype": "Supplier",
				"supplier_group": "All Supplier Groups",
				"supplier_type": "Company",
				"supplier_name": "Poore Simon's",
			}
		).insert(ignore_if_duplicate=True)
	except vmraid.DuplicateEntryError:
		pass

	try:
		vmraid.get_doc(
			{
				"doctype": "Customer",
				"customer_group": "All Customer Groups",
				"customer_type": "Company",
				"customer_name": "Poore Simon's",
			}
		).insert(ignore_if_duplicate=True)
	except vmraid.DuplicateEntryError:
		pass

	pi = make_purchase_invoice(supplier="Poore Simon's", qty=1, rate=3900, is_paid=1, do_not_save=1)
	pi.cash_bank_account = "_Test Bank - _TC"
	pi.insert()
	pi.submit()
	pe = get_payment_entry("Purchase Invoice", pi.name, bank_account="_Test Bank - _TC")
	pe.reference_no = "Poore Simon's Oct 18"
	pe.reference_date = "2018-10-28"
	pe.paid_amount = 690
	pe.received_amount = 690
	pe.insert()
	pe.submit()

	si = create_sales_invoice(customer="Poore Simon's", qty=1, rate=3900)
	pe = get_payment_entry("Sales Invoice", si.name, bank_account="_Test Bank - _TC")
	pe.reference_no = "Poore Simon's Oct 18"
	pe.reference_date = "2018-10-28"
	pe.insert()
	pe.submit()

	try:
		vmraid.get_doc(
			{
				"doctype": "Customer",
				"customer_group": "All Customer Groups",
				"customer_type": "Company",
				"customer_name": "Fayva",
			}
		).insert(ignore_if_duplicate=True)
	except vmraid.DuplicateEntryError:
		pass

	mode_of_payment = vmraid.get_doc({"doctype": "Mode of Payment", "name": "Cash"})

	if not vmraid.db.get_value(
		"Mode of Payment Account", {"company": "_Test Company", "parent": "Cash"}
	):
		mode_of_payment.append(
			"accounts", {"company": "_Test Company", "default_account": "_Test Bank - _TC"}
		)
		mode_of_payment.save()

	si = create_sales_invoice(customer="Fayva", qty=1, rate=109080, do_not_save=1)
	si.is_pos = 1
	si.append(
		"payments", {"mode_of_payment": "Cash", "account": "_Test Bank - _TC", "amount": 109080}
	)
	si.insert()
	si.submit()
