# Copyright (c) 2015, VMRaid and contributors
# For license information, please see license.txt


import vmraid
from vmraid import _
from vmraid.model.document import Document
from vmraid.utils.csvutils import getlink


class Guardian(Document):
	def __setup__(self):
		self.onload()

	def onload(self):
		"""Load Students for quick view"""
		self.load_students()

	def load_students(self):
		"""Load `students` from the database"""
		self.students = []
		students = vmraid.get_all("Student Guardian", filters={"guardian": self.name}, fields=["parent"])
		for student in students:
			self.append(
				"students",
				{
					"student": student.parent,
					"student_name": vmraid.db.get_value("Student", student.parent, "title"),
				},
			)

	def validate(self):
		self.students = []


@vmraid.whitelist()
def invite_guardian(guardian):
	guardian_doc = vmraid.get_doc("Guardian", guardian)
	if not guardian_doc.email_address:
		vmraid.throw(_("Please set Email Address"))
	else:
		guardian_as_user = vmraid.get_value("User", dict(email=guardian_doc.email_address))
		if guardian_as_user:
			vmraid.msgprint(_("User {0} already exists").format(getlink("User", guardian_as_user)))
			return guardian_as_user
		else:
			user = vmraid.get_doc(
				{
					"doctype": "User",
					"first_name": guardian_doc.guardian_name,
					"email": guardian_doc.email_address,
					"user_type": "Website User",
					"send_welcome_email": 1,
				}
			).insert(ignore_permissions=True)
			vmraid.msgprint(_("User {0} created").format(getlink("User", user.name)))
			return user.name
