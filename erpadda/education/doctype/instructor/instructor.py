# Copyright (c) 2015, VMRaid Technologies and contributors
# For license information, please see license.txt


import vmraid
from vmraid import _
from vmraid.model.document import Document
from vmraid.model.naming import set_name_by_naming_series


class Instructor(Document):
	def autoname(self):
		naming_method = vmraid.db.get_value("Education Settings", None, "instructor_created_by")
		if not naming_method:
			vmraid.throw(_("Please setup Instructor Naming System in Education > Education Settings"))
		else:
			if naming_method == "Naming Series":
				set_name_by_naming_series(self)
			elif naming_method == "Employee Number":
				if not self.employee:
					vmraid.throw(_("Please select Employee"))
				self.name = self.employee
			elif naming_method == "Full Name":
				self.name = self.instructor_name

	def validate(self):
		self.validate_duplicate_employee()

	def validate_duplicate_employee(self):
		if self.employee and vmraid.db.get_value(
			"Instructor", {"employee": self.employee, "name": ["!=", self.name]}, "name"
		):
			vmraid.throw(_("Employee ID is linked with another instructor"))


def get_timeline_data(doctype, name):
	"""Return timeline for course schedule"""
	return dict(
		vmraid.db.sql(
			"""
			SELECT unix_timestamp(`schedule_date`), count(*)
			FROM `tabCourse Schedule`
			WHERE
				instructor=%s and
				`schedule_date` > date_sub(curdate(), interval 1 year)
			GROUP BY schedule_date
		""",
			name,
		)
	)
