# Copyright (c) 2018, VMRaid and contributors
# For license information, please see license.txt


import vmraid
from vmraid import _
from vmraid.model.document import Document
from vmraid.utils import getdate

from erpadda.hr.utils import validate_active_employee


class RetentionBonus(Document):
	def validate(self):
		validate_active_employee(self.employee)
		if getdate(self.bonus_payment_date) < getdate():
			vmraid.throw(_("Bonus Payment Date cannot be a past date"))

	def on_submit(self):
		company = vmraid.db.get_value("Employee", self.employee, "company")
		additional_salary = self.get_additional_salary()

		if not additional_salary:
			additional_salary = vmraid.new_doc("Additional Salary")
			additional_salary.employee = self.employee
			additional_salary.salary_component = self.salary_component
			additional_salary.amount = self.bonus_amount
			additional_salary.payroll_date = self.bonus_payment_date
			additional_salary.company = company
			additional_salary.overwrite_salary_structure_amount = 0
			additional_salary.ref_doctype = self.doctype
			additional_salary.ref_docname = self.name
			additional_salary.submit()
			# self.db_set('additional_salary', additional_salary.name)

		else:
			bonus_added = (
				vmraid.db.get_value("Additional Salary", additional_salary, "amount") + self.bonus_amount
			)
			vmraid.db.set_value("Additional Salary", additional_salary, "amount", bonus_added)
			self.db_set("additional_salary", additional_salary)

	def on_cancel(self):

		additional_salary = self.get_additional_salary()
		if self.additional_salary:
			bonus_removed = (
				vmraid.db.get_value("Additional Salary", self.additional_salary, "amount") - self.bonus_amount
			)
			if bonus_removed == 0:
				vmraid.get_doc("Additional Salary", self.additional_salary).cancel()
			else:
				vmraid.db.set_value("Additional Salary", self.additional_salary, "amount", bonus_removed)

			# self.db_set('additional_salary', '')

	def get_additional_salary(self):
		return vmraid.db.exists(
			"Additional Salary",
			{
				"employee": self.employee,
				"salary_component": self.salary_component,
				"payroll_date": self.bonus_payment_date,
				"company": self.company,
				"docstatus": 1,
				"ref_doctype": self.doctype,
				"ref_docname": self.name,
			},
		)
