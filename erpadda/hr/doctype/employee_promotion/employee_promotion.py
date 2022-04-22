# Copyright (c) 2018, VMRaid and contributors
# For license information, please see license.txt


import vmraid
from vmraid import _
from vmraid.model.document import Document
from vmraid.utils import getdate

from erpadda.hr.utils import update_employee_work_history, validate_active_employee


class EmployeePromotion(Document):
	def validate(self):
		validate_active_employee(self.employee)

	def before_submit(self):
		if getdate(self.promotion_date) > getdate():
			vmraid.throw(
				_("Employee Promotion cannot be submitted before Promotion Date"),
				vmraid.DocstatusTransitionError,
			)

	def on_submit(self):
		employee = vmraid.get_doc("Employee", self.employee)
		employee = update_employee_work_history(
			employee, self.promotion_details, date=self.promotion_date
		)
		employee.save()

	def on_cancel(self):
		employee = vmraid.get_doc("Employee", self.employee)
		employee = update_employee_work_history(employee, self.promotion_details, cancel=True)
		employee.save()
