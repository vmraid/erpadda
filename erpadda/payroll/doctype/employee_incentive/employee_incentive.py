# Copyright (c) 2018, VMRaid and contributors
# For license information, please see license.txt


import vmraid
from vmraid import _
from vmraid.model.document import Document

from erpadda.hr.utils import validate_active_employee


class EmployeeIncentive(Document):
	def validate(self):
		validate_active_employee(self.employee)
		self.validate_salary_structure()

	def validate_salary_structure(self):
		if not vmraid.db.exists("Salary Structure Assignment", {"employee": self.employee}):
			vmraid.throw(
				_("There is no Salary Structure assigned to {0}. First assign a Salary Stucture.").format(
					self.employee
				)
			)

	def on_submit(self):
		company = vmraid.db.get_value("Employee", self.employee, "company")

		additional_salary = vmraid.new_doc("Additional Salary")
		additional_salary.employee = self.employee
		additional_salary.currency = self.currency
		additional_salary.salary_component = self.salary_component
		additional_salary.overwrite_salary_structure_amount = 0
		additional_salary.amount = self.incentive_amount
		additional_salary.payroll_date = self.payroll_date
		additional_salary.company = company
		additional_salary.ref_doctype = self.doctype
		additional_salary.ref_docname = self.name
		additional_salary.submit()
