# Copyright (c) 2018, VMRaid and contributors
# For license information, please see license.txt


from vmraid.model.document import Document

from erpadda.hr.utils import validate_active_employee


class TravelRequest(Document):
	def validate(self):
		validate_active_employee(self.employee)
