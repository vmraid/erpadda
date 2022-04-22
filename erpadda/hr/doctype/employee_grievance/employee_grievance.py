# Copyright (c) 2021, VMRaid and contributors
# For license information, please see license.txt

import vmraid
from vmraid import _, bold
from vmraid.model.document import Document


class EmployeeGrievance(Document):
	def on_submit(self):
		if self.status not in ["Invalid", "Resolved"]:
			vmraid.throw(
				_("Only Employee Grievance with status {0} or {1} can be submitted").format(
					bold("Invalid"), bold("Resolved")
				)
			)
