# Copyright (c) 2018, VMRaid and Contributors
# See license.txt

import unittest

import vmraid

import erpadda
from erpadda.hr.doctype.employee.test_employee import make_employee
from erpadda.hr.utils import DuplicateDeclarationError


class TestEmployeeTaxExemptionDeclaration(unittest.TestCase):
	def setUp(self):
		make_employee("employee@taxexepmtion.com")
		make_employee("employee1@taxexepmtion.com")
		create_payroll_period()
		create_exemption_category()
		vmraid.db.sql("""delete from `tabEmployee Tax Exemption Declaration`""")

	def test_duplicate_category_in_declaration(self):
		declaration = vmraid.get_doc(
			{
				"doctype": "Employee Tax Exemption Declaration",
				"employee": vmraid.get_value("Employee", {"user_id": "employee@taxexepmtion.com"}, "name"),
				"company": erpadda.get_default_company(),
				"payroll_period": "_Test Payroll Period",
				"currency": erpadda.get_default_currency(),
				"declarations": [
					dict(
						exemption_sub_category="_Test Sub Category",
						exemption_category="_Test Category",
						amount=100000,
					),
					dict(
						exemption_sub_category="_Test Sub Category",
						exemption_category="_Test Category",
						amount=50000,
					),
				],
			}
		)
		self.assertRaises(vmraid.ValidationError, declaration.save)

	def test_duplicate_entry_for_payroll_period(self):
		declaration = vmraid.get_doc(
			{
				"doctype": "Employee Tax Exemption Declaration",
				"employee": vmraid.get_value("Employee", {"user_id": "employee@taxexepmtion.com"}, "name"),
				"company": erpadda.get_default_company(),
				"payroll_period": "_Test Payroll Period",
				"currency": erpadda.get_default_currency(),
				"declarations": [
					dict(
						exemption_sub_category="_Test Sub Category",
						exemption_category="_Test Category",
						amount=100000,
					),
					dict(
						exemption_sub_category="_Test1 Sub Category",
						exemption_category="_Test Category",
						amount=50000,
					),
				],
			}
		).insert()

		duplicate_declaration = vmraid.get_doc(
			{
				"doctype": "Employee Tax Exemption Declaration",
				"employee": vmraid.get_value("Employee", {"user_id": "employee@taxexepmtion.com"}, "name"),
				"company": erpadda.get_default_company(),
				"payroll_period": "_Test Payroll Period",
				"currency": erpadda.get_default_currency(),
				"declarations": [
					dict(
						exemption_sub_category="_Test Sub Category",
						exemption_category="_Test Category",
						amount=100000,
					)
				],
			}
		)
		self.assertRaises(DuplicateDeclarationError, duplicate_declaration.insert)
		duplicate_declaration.employee = vmraid.get_value(
			"Employee", {"user_id": "employee1@taxexepmtion.com"}, "name"
		)
		self.assertTrue(duplicate_declaration.insert)

	def test_exemption_amount(self):
		declaration = vmraid.get_doc(
			{
				"doctype": "Employee Tax Exemption Declaration",
				"employee": vmraid.get_value("Employee", {"user_id": "employee@taxexepmtion.com"}, "name"),
				"company": erpadda.get_default_company(),
				"payroll_period": "_Test Payroll Period",
				"currency": erpadda.get_default_currency(),
				"declarations": [
					dict(
						exemption_sub_category="_Test Sub Category",
						exemption_category="_Test Category",
						amount=80000,
					),
					dict(
						exemption_sub_category="_Test1 Sub Category",
						exemption_category="_Test Category",
						amount=60000,
					),
				],
			}
		).insert()

		self.assertEqual(declaration.total_exemption_amount, 100000)


def create_payroll_period(**args):
	args = vmraid._dict(args)
	name = args.name or "_Test Payroll Period"
	if not vmraid.db.exists("Payroll Period", name):
		from datetime import date

		payroll_period = vmraid.get_doc(
			dict(
				doctype="Payroll Period",
				name=name,
				company=args.company or erpadda.get_default_company(),
				start_date=args.start_date or date(date.today().year, 1, 1),
				end_date=args.end_date or date(date.today().year, 12, 31),
			)
		).insert()
		return payroll_period
	else:
		return vmraid.get_doc("Payroll Period", name)


def create_exemption_category():
	if not vmraid.db.exists("Employee Tax Exemption Category", "_Test Category"):
		category = vmraid.get_doc(
			{
				"doctype": "Employee Tax Exemption Category",
				"name": "_Test Category",
				"deduction_component": "Income Tax",
				"max_amount": 100000,
			}
		).insert()
	if not vmraid.db.exists("Employee Tax Exemption Sub Category", "_Test Sub Category"):
		vmraid.get_doc(
			{
				"doctype": "Employee Tax Exemption Sub Category",
				"name": "_Test Sub Category",
				"exemption_category": "_Test Category",
				"max_amount": 100000,
				"is_active": 1,
			}
		).insert()
	if not vmraid.db.exists("Employee Tax Exemption Sub Category", "_Test1 Sub Category"):
		vmraid.get_doc(
			{
				"doctype": "Employee Tax Exemption Sub Category",
				"name": "_Test1 Sub Category",
				"exemption_category": "_Test Category",
				"max_amount": 50000,
				"is_active": 1,
			}
		).insert()
