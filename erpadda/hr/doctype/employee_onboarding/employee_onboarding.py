# Copyright (c) 2018, VMRaid and contributors
# For license information, please see license.txt


import vmraid
from vmraid import _
from vmraid.model.mapper import get_mapped_doc

from erpadda.controllers.employee_boarding_controller import EmployeeBoardingController


class IncompleteTaskError(vmraid.ValidationError):
	pass


class EmployeeOnboarding(EmployeeBoardingController):
	def validate(self):
		super(EmployeeOnboarding, self).validate()
		self.set_employee()
		self.validate_duplicate_employee_onboarding()

	def set_employee(self):
		if not self.employee:
			self.employee = vmraid.db.get_value("Employee", {"job_applicant": self.job_applicant}, "name")

	def validate_duplicate_employee_onboarding(self):
		emp_onboarding = vmraid.db.exists(
			"Employee Onboarding", {"job_applicant": self.job_applicant, "docstatus": ("!=", 2)}
		)
		if emp_onboarding and emp_onboarding != self.name:
			vmraid.throw(
				_("Employee Onboarding: {0} already exists for Job Applicant: {1}").format(
					vmraid.bold(emp_onboarding), vmraid.bold(self.job_applicant)
				)
			)

	def validate_employee_creation(self):
		if self.docstatus != 1:
			vmraid.throw(_("Submit this to create the Employee record"))
		else:
			for activity in self.activities:
				if not activity.required_for_employee_creation:
					continue
				else:
					task_status = vmraid.db.get_value("Task", activity.task, "status")
					if task_status not in ["Completed", "Cancelled"]:
						vmraid.throw(
							_("All the mandatory tasks for employee creation are not completed yet."),
							IncompleteTaskError,
						)

	def on_submit(self):
		super(EmployeeOnboarding, self).on_submit()

	def on_update_after_submit(self):
		self.create_task_and_notify_user()

	def on_cancel(self):
		super(EmployeeOnboarding, self).on_cancel()


@vmraid.whitelist()
def make_employee(source_name, target_doc=None):
	doc = vmraid.get_doc("Employee Onboarding", source_name)
	doc.validate_employee_creation()

	def set_missing_values(source, target):
		target.personal_email = vmraid.db.get_value("Job Applicant", source.job_applicant, "email_id")
		target.status = "Active"

	doc = get_mapped_doc(
		"Employee Onboarding",
		source_name,
		{
			"Employee Onboarding": {
				"doctype": "Employee",
				"field_map": {
					"first_name": "employee_name",
					"employee_grade": "grade",
				},
			}
		},
		target_doc,
		set_missing_values,
	)
	return doc
