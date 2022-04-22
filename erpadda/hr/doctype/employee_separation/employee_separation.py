# Copyright (c) 2018, VMRaid and contributors
# For license information, please see license.txt


from erpadda.controllers.employee_boarding_controller import EmployeeBoardingController


class EmployeeSeparation(EmployeeBoardingController):
	def validate(self):
		super(EmployeeSeparation, self).validate()

	def on_submit(self):
		super(EmployeeSeparation, self).on_submit()

	def on_update_after_submit(self):
		self.create_task_and_notify_user()

	def on_cancel(self):
		super(EmployeeSeparation, self).on_cancel()
