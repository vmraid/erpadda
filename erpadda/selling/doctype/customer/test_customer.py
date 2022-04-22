# Copyright (c) 2015, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid
from vmraid.test_runner import make_test_records
from vmraid.tests.utils import VMRaidTestCase
from vmraid.utils import flt

from erpadda.accounts.party import get_due_date
from erpadda.exceptions import PartyDisabled, PartyFrozen
from erpadda.selling.doctype.customer.customer import get_credit_limit, get_customer_outstanding
from erpadda.tests.utils import create_test_contact_and_address

test_ignore = ["Price List"]
test_dependencies = ["Payment Term", "Payment Terms Template"]
test_records = vmraid.get_test_records("Customer")


class TestCustomer(VMRaidTestCase):
	def setUp(self):
		if not vmraid.get_value("Item", "_Test Item"):
			make_test_records("Item")

	def tearDown(self):
		set_credit_limit("_Test Customer", "_Test Company", 0)

	def test_get_customer_group_details(self):
		doc = vmraid.new_doc("Customer Group")
		doc.customer_group_name = "_Testing Customer Group"
		doc.payment_terms = "_Test Payment Term Template 3"
		doc.accounts = []
		doc.default_price_list = "Standard Buying"
		doc.credit_limits = []
		test_account_details = {
			"company": "_Test Company",
			"account": "Creditors - _TC",
		}
		test_credit_limits = {"company": "_Test Company", "credit_limit": 350000}
		doc.append("accounts", test_account_details)
		doc.append("credit_limits", test_credit_limits)
		doc.insert()

		c_doc = vmraid.new_doc("Customer")
		c_doc.customer_name = "Testing Customer"
		c_doc.customer_group = "_Testing Customer Group"
		c_doc.payment_terms = c_doc.default_price_list = ""
		c_doc.accounts = []
		c_doc.credit_limits = []
		c_doc.insert()
		c_doc.get_customer_group_details()
		self.assertEqual(c_doc.payment_terms, "_Test Payment Term Template 3")

		self.assertEqual(c_doc.accounts[0].company, "_Test Company")
		self.assertEqual(c_doc.accounts[0].account, "Creditors - _TC")

		self.assertEqual(c_doc.credit_limits[0].company, "_Test Company")
		self.assertEqual(c_doc.credit_limits[0].credit_limit, 350000)
		c_doc.delete()
		doc.delete()

	def test_party_details(self):
		from erpadda.accounts.party import get_party_details

		to_check = {
			"selling_price_list": None,
			"customer_group": "_Test Customer Group",
			"contact_designation": None,
			"customer_address": "_Test Address for Customer-Office",
			"contact_department": None,
			"contact_email": "test_contact_customer@example.com",
			"contact_mobile": None,
			"sales_team": [],
			"contact_display": "_Test Contact for _Test Customer",
			"contact_person": "_Test Contact for _Test Customer-_Test Customer",
			"territory": "_Test Territory",
			"contact_phone": "+91 0000000000",
			"customer_name": "_Test Customer",
		}

		create_test_contact_and_address()

		vmraid.db.set_value(
			"Contact", "_Test Contact for _Test Customer-_Test Customer", "is_primary_contact", 1
		)

		details = get_party_details("_Test Customer")

		for key, value in to_check.items():
			val = details.get(key)
			if not val and not isinstance(val, list):
				val = None

			self.assertEqual(value, val)

	def test_party_details_tax_category(self):
		from erpadda.accounts.party import get_party_details

		vmraid.delete_doc_if_exists("Address", "_Test Address With Tax Category-Billing")
		vmraid.delete_doc_if_exists("Address", "_Test Address With Tax Category-Shipping")

		# Tax Category without Address
		details = get_party_details("_Test Customer With Tax Category")
		self.assertEqual(details.tax_category, "_Test Tax Category 1")

		billing_address = vmraid.get_doc(
			dict(
				doctype="Address",
				address_title="_Test Address With Tax Category",
				tax_category="_Test Tax Category 2",
				address_type="Billing",
				address_line1="Station Road",
				city="_Test City",
				country="India",
				links=[dict(link_doctype="Customer", link_name="_Test Customer With Tax Category")],
			)
		).insert()
		shipping_address = vmraid.get_doc(
			dict(
				doctype="Address",
				address_title="_Test Address With Tax Category",
				tax_category="_Test Tax Category 3",
				address_type="Shipping",
				address_line1="Station Road",
				city="_Test City",
				country="India",
				links=[dict(link_doctype="Customer", link_name="_Test Customer With Tax Category")],
			)
		).insert()

		settings = vmraid.get_single("Accounts Settings")
		rollback_setting = settings.determine_address_tax_category_from

		# Tax Category from Billing Address
		settings.determine_address_tax_category_from = "Billing Address"
		settings.save()
		details = get_party_details("_Test Customer With Tax Category")
		self.assertEqual(details.tax_category, "_Test Tax Category 2")

		# Tax Category from Shipping Address
		settings.determine_address_tax_category_from = "Shipping Address"
		settings.save()
		details = get_party_details("_Test Customer With Tax Category")
		self.assertEqual(details.tax_category, "_Test Tax Category 3")

		# Rollback
		settings.determine_address_tax_category_from = rollback_setting
		settings.save()
		billing_address.delete()
		shipping_address.delete()

	def test_rename(self):
		# delete communication linked to these 2 customers

		new_name = "_Test Customer 1 Renamed"
		for name in ("_Test Customer 1", new_name):
			vmraid.db.sql(
				"""delete from `tabComment`
				where reference_doctype=%s and reference_name=%s""",
				("Customer", name),
			)

		# add comments
		comment = vmraid.get_doc("Customer", "_Test Customer 1").add_comment(
			"Comment", "Test Comment for Rename"
		)

		# rename
		vmraid.rename_doc("Customer", "_Test Customer 1", new_name)

		# check if customer renamed
		self.assertTrue(vmraid.db.exists("Customer", new_name))
		self.assertFalse(vmraid.db.exists("Customer", "_Test Customer 1"))

		# test that comment gets linked to renamed doc
		self.assertEqual(
			vmraid.db.get_value(
				"Comment",
				{
					"reference_doctype": "Customer",
					"reference_name": new_name,
					"content": "Test Comment for Rename",
				},
			),
			comment.name,
		)

		# rename back to original
		vmraid.rename_doc("Customer", new_name, "_Test Customer 1")

		vmraid.db.rollback()

	def test_freezed_customer(self):
		make_test_records("Item")

		vmraid.db.set_value("Customer", "_Test Customer", "is_frozen", 1)

		from erpadda.selling.doctype.sales_order.test_sales_order import make_sales_order

		so = make_sales_order(do_not_save=True)

		self.assertRaises(PartyFrozen, so.save)

		vmraid.db.set_value("Customer", "_Test Customer", "is_frozen", 0)

		so.save()

	def test_delete_customer_contact(self):
		customer = vmraid.get_doc(get_customer_dict("_Test Customer for delete")).insert(
			ignore_permissions=True
		)

		customer.mobile_no = "8989889890"
		customer.save()
		self.assertTrue(customer.customer_primary_contact)
		vmraid.delete_doc("Customer", customer.name)

	def test_disabled_customer(self):
		make_test_records("Item")

		vmraid.db.set_value("Customer", "_Test Customer", "disabled", 1)

		from erpadda.selling.doctype.sales_order.test_sales_order import make_sales_order

		so = make_sales_order(do_not_save=True)

		self.assertRaises(PartyDisabled, so.save)

		vmraid.db.set_value("Customer", "_Test Customer", "disabled", 0)

		so.save()

	def test_duplicate_customer(self):
		vmraid.db.sql("delete from `tabCustomer` where customer_name='_Test Customer 1'")

		if not vmraid.db.get_value("Customer", "_Test Customer 1"):
			test_customer_1 = vmraid.get_doc(get_customer_dict("_Test Customer 1")).insert(
				ignore_permissions=True
			)
		else:
			test_customer_1 = vmraid.get_doc("Customer", "_Test Customer 1")

		duplicate_customer = vmraid.get_doc(get_customer_dict("_Test Customer 1")).insert(
			ignore_permissions=True
		)

		self.assertEqual("_Test Customer 1", test_customer_1.name)
		self.assertEqual("_Test Customer 1 - 1", duplicate_customer.name)
		self.assertEqual(test_customer_1.customer_name, duplicate_customer.customer_name)

	def get_customer_outstanding_amount(self):
		from erpadda.selling.doctype.sales_order.test_sales_order import make_sales_order

		outstanding_amt = get_customer_outstanding("_Test Customer", "_Test Company")

		# If outstanding is negative make a transaction to get positive outstanding amount
		if outstanding_amt > 0.0:
			return outstanding_amt

		item_qty = int((abs(outstanding_amt) + 200) / 100)
		make_sales_order(qty=item_qty)
		return get_customer_outstanding("_Test Customer", "_Test Company")

	def test_customer_credit_limit(self):
		from erpadda.accounts.doctype.sales_invoice.test_sales_invoice import create_sales_invoice
		from erpadda.selling.doctype.sales_order.sales_order import make_sales_invoice
		from erpadda.selling.doctype.sales_order.test_sales_order import make_sales_order
		from erpadda.stock.doctype.delivery_note.test_delivery_note import create_delivery_note

		outstanding_amt = self.get_customer_outstanding_amount()
		credit_limit = get_credit_limit("_Test Customer", "_Test Company")

		if outstanding_amt <= 0.0:
			item_qty = int((abs(outstanding_amt) + 200) / 100)
			make_sales_order(qty=item_qty)

		if not credit_limit:
			set_credit_limit("_Test Customer", "_Test Company", outstanding_amt - 50)

		# Sales Order
		so = make_sales_order(do_not_submit=True)
		self.assertRaises(vmraid.ValidationError, so.submit)

		# Delivery Note
		dn = create_delivery_note(do_not_submit=True)
		self.assertRaises(vmraid.ValidationError, dn.submit)

		# Sales Invoice
		si = create_sales_invoice(do_not_submit=True)
		self.assertRaises(vmraid.ValidationError, si.submit)

		if credit_limit > outstanding_amt:
			set_credit_limit("_Test Customer", "_Test Company", credit_limit)

		# Makes Sales invoice from Sales Order
		so.save(ignore_permissions=True)
		si = make_sales_invoice(so.name)
		si.save(ignore_permissions=True)
		self.assertRaises(vmraid.ValidationError, make_sales_order)

	def test_customer_credit_limit_on_change(self):
		outstanding_amt = self.get_customer_outstanding_amount()
		customer = vmraid.get_doc("Customer", "_Test Customer")
		customer.append(
			"credit_limits", {"credit_limit": flt(outstanding_amt - 100), "company": "_Test Company"}
		)

		""" define new credit limit for same company """
		customer.append(
			"credit_limits", {"credit_limit": flt(outstanding_amt - 100), "company": "_Test Company"}
		)
		self.assertRaises(vmraid.ValidationError, customer.save)

	def test_customer_payment_terms(self):
		vmraid.db.set_value(
			"Customer", "_Test Customer With Template", "payment_terms", "_Test Payment Term Template 3"
		)

		due_date = get_due_date("2016-01-22", "Customer", "_Test Customer With Template")
		self.assertEqual(due_date, "2016-02-21")

		due_date = get_due_date("2017-01-22", "Customer", "_Test Customer With Template")
		self.assertEqual(due_date, "2017-02-21")

		vmraid.db.set_value(
			"Customer", "_Test Customer With Template", "payment_terms", "_Test Payment Term Template 1"
		)

		due_date = get_due_date("2016-01-22", "Customer", "_Test Customer With Template")
		self.assertEqual(due_date, "2016-02-29")

		due_date = get_due_date("2017-01-22", "Customer", "_Test Customer With Template")
		self.assertEqual(due_date, "2017-02-28")

		vmraid.db.set_value("Customer", "_Test Customer With Template", "payment_terms", "")

		# No default payment term template attached
		due_date = get_due_date("2016-01-22", "Customer", "_Test Customer")
		self.assertEqual(due_date, "2016-01-22")

		due_date = get_due_date("2017-01-22", "Customer", "_Test Customer")
		self.assertEqual(due_date, "2017-01-22")


def get_customer_dict(customer_name):
	return {
		"customer_group": "_Test Customer Group",
		"customer_name": customer_name,
		"customer_type": "Individual",
		"doctype": "Customer",
		"territory": "_Test Territory",
	}


def set_credit_limit(customer, company, credit_limit):
	customer = vmraid.get_doc("Customer", customer)
	existing_row = None
	for d in customer.credit_limits:
		if d.company == company:
			existing_row = d
			d.credit_limit = credit_limit
			d.db_update()
			break

	if not existing_row:
		customer.append("credit_limits", {"company": company, "credit_limit": credit_limit})
		customer.credit_limits[-1].db_insert()


def create_internal_customer(customer_name, represents_company, allowed_to_interact_with):
	if not vmraid.db.exists("Customer", customer_name):
		customer = vmraid.get_doc(
			{
				"doctype": "Customer",
				"customer_group": "_Test Customer Group",
				"customer_name": customer_name,
				"customer_type": "Individual",
				"territory": "_Test Territory",
				"is_internal_customer": 1,
				"represents_company": represents_company,
			}
		)

		customer.append("companies", {"company": allowed_to_interact_with})

		customer.insert()
		customer_name = customer.name
	else:
		customer_name = vmraid.db.get_value("Customer", customer_name)

	return customer_name
