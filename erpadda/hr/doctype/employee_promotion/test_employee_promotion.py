# Copyright (c) 2018, VMRaid and Contributors
# See license.txt

import unittest

import vmraid
from vmraid.utils import add_days, getdate

from erpadda.payroll.doctype.salary_structure.test_salary_structure import make_employee


class TestEmployeePromotion(unittest.TestCase):
	def setUp(self):
		self.employee = make_employee("employee@promotions.com")
		vmraid.db.sql("""delete from `tabEmployee Promotion`""")

	def test_submit_before_promotion_date(self):
		promotion_obj = vmraid.get_doc(
			{
				"doctype": "Employee Promotion",
				"employee": self.employee,
				"promotion_details": [
					{
						"property": "Designation",
						"current": "Software Developer",
						"new": "Project Manager",
						"fieldname": "designation",
					}
				],
			}
		)
		promotion_obj.promotion_date = add_days(getdate(), 1)
		promotion_obj.save()
		self.assertRaises(vmraid.DocstatusTransitionError, promotion_obj.submit)
		promotion = vmraid.get_doc("Employee Promotion", promotion_obj.name)
		promotion.promotion_date = getdate()
		promotion.submit()
		self.assertEqual(promotion.docstatus, 1)
