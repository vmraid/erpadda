# Copyright (c) 2018, VMRaid and contributors
# For license information, please see license.txt


import vmraid
from vmraid import _
from vmraid.model.document import Document
from vmraid.utils import getdate

from erpadda.hr.utils import validate_overlap


class LeavePeriod(Document):
	def validate(self):
		self.validate_dates()
		validate_overlap(self, self.from_date, self.to_date, self.company)

	def validate_dates(self):
		if getdate(self.from_date) >= getdate(self.to_date):
			vmraid.throw(_("To date can not be equal or less than from date"))
