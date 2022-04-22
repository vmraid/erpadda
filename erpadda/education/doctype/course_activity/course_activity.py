# Copyright (c) 2018, VMRaid and contributors
# For license information, please see license.txt


import vmraid
from vmraid import _
from vmraid.model.document import Document


class CourseActivity(Document):
	def validate(self):
		self.check_if_enrolled()

	def check_if_enrolled(self):
		if vmraid.db.exists("Course Enrollment", self.enrollment):
			return True
		else:
			vmraid.throw(_("Course Enrollment {0} does not exists").format(self.enrollment))
