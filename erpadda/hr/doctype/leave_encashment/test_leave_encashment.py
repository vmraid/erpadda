# Copyright (c) 2018, VMRaid and Contributors
# See license.txt

import unittest

import vmraid
from vmraid.utils import add_months, today

from erpadda.hr.doctype.employee.test_employee import make_employee
from erpadda.hr.doctype.leave_period.test_leave_period import create_leave_period
from erpadda.hr.doctype.leave_policy.test_leave_policy import create_leave_policy
from erpadda.hr.doctype.leave_policy_assignment.leave_policy_assignment import (
	create_assignment_for_multiple_employees,
)
from erpadda.payroll.doctype.salary_structure.test_salary_structure import make_salary_structure

test_dependencies = ["Leave Type"]


class TestLeaveEncashment(unittest.TestCase):
	def setUp(self):
		vmraid.db.sql("""delete from `tabLeave Period`""")
		vmraid.db.sql("""delete from `tabLeave Policy Assignment`""")
		vmraid.db.sql("""delete from `tabLeave Allocation`""")
		vmraid.db.sql("""delete from `tabLeave Ledger Entry`""")
		vmraid.db.sql("""delete from `tabAdditional Salary`""")

		# create the leave policy
		leave_policy = create_leave_policy(
			leave_type="_Test Leave Type Encashment", annual_allocation=10
		)
		leave_policy.submit()

		# create employee, salary structure and assignment
		self.employee = make_employee("test_employee_encashment@example.com")

		self.leave_period = create_leave_period(add_months(today(), -3), add_months(today(), 3))

		data = {
			"assignment_based_on": "Leave Period",
			"leave_policy": leave_policy.name,
			"leave_period": self.leave_period.name,
		}

		leave_policy_assignments = create_assignment_for_multiple_employees(
			[self.employee], vmraid._dict(data)
		)

		salary_structure = make_salary_structure(
			"Salary Structure for Encashment",
			"Monthly",
			self.employee,
			other_details={"leave_encashment_amount_per_day": 50},
		)

	def tearDown(self):
		for dt in [
			"Leave Period",
			"Leave Allocation",
			"Leave Ledger Entry",
			"Additional Salary",
			"Leave Encashment",
			"Salary Structure",
			"Leave Policy",
		]:
			vmraid.db.sql("delete from `tab%s`" % dt)

	def test_leave_balance_value_and_amount(self):
		vmraid.db.sql("""delete from `tabLeave Encashment`""")
		leave_encashment = vmraid.get_doc(
			dict(
				doctype="Leave Encashment",
				employee=self.employee,
				leave_type="_Test Leave Type Encashment",
				leave_period=self.leave_period.name,
				payroll_date=today(),
				currency="INR",
			)
		).insert()

		self.assertEqual(leave_encashment.leave_balance, 10)
		self.assertEqual(leave_encashment.encashable_days, 5)
		self.assertEqual(leave_encashment.encashment_amount, 250)

		leave_encashment.submit()

		# assert links
		add_sal = vmraid.get_all("Additional Salary", filters={"ref_docname": leave_encashment.name})[0]
		self.assertTrue(add_sal)

	def test_creation_of_leave_ledger_entry_on_submit(self):
		vmraid.db.sql("""delete from `tabLeave Encashment`""")
		leave_encashment = vmraid.get_doc(
			dict(
				doctype="Leave Encashment",
				employee=self.employee,
				leave_type="_Test Leave Type Encashment",
				leave_period=self.leave_period.name,
				payroll_date=today(),
				currency="INR",
			)
		).insert()

		leave_encashment.submit()

		leave_ledger_entry = vmraid.get_all(
			"Leave Ledger Entry", fields="*", filters=dict(transaction_name=leave_encashment.name)
		)

		self.assertEqual(len(leave_ledger_entry), 1)
		self.assertEqual(leave_ledger_entry[0].employee, leave_encashment.employee)
		self.assertEqual(leave_ledger_entry[0].leave_type, leave_encashment.leave_type)
		self.assertEqual(leave_ledger_entry[0].leaves, leave_encashment.encashable_days * -1)

		# check if leave ledger entry is deleted on cancellation

		vmraid.db.sql(
			"Delete from `tabAdditional Salary` WHERE ref_docname = %s", (leave_encashment.name)
		)

		leave_encashment.cancel()
		self.assertFalse(
			vmraid.db.exists("Leave Ledger Entry", {"transaction_name": leave_encashment.name})
		)
