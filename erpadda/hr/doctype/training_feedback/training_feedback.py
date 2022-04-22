# Copyright (c) 2015, VMRaid and contributors
# For license information, please see license.txt


import vmraid
from vmraid import _
from vmraid.model.document import Document


class TrainingFeedback(Document):
	def validate(self):
		training_event = vmraid.get_doc("Training Event", self.training_event)
		if training_event.docstatus != 1:
			vmraid.throw(_("{0} must be submitted").format(_("Training Event")))

		emp_event_details = vmraid.db.get_value(
			"Training Event Employee",
			{"parent": self.training_event, "employee": self.employee},
			["name", "attendance"],
			as_dict=True,
		)

		if not emp_event_details:
			vmraid.throw(
				_("Employee {0} not found in Training Event Participants.").format(
					vmraid.bold(self.employee_name)
				)
			)

		if emp_event_details.attendance == "Absent":
			vmraid.throw(_("Feedback cannot be recorded for an absent Employee."))

	def on_submit(self):
		employee = vmraid.db.get_value(
			"Training Event Employee", {"parent": self.training_event, "employee": self.employee}
		)

		if employee:
			vmraid.db.set_value("Training Event Employee", employee, "status", "Feedback Submitted")

	def on_cancel(self):
		employee = vmraid.db.get_value(
			"Training Event Employee", {"parent": self.training_event, "employee": self.employee}
		)

		if employee:
			vmraid.db.set_value("Training Event Employee", employee, "status", "Completed")
