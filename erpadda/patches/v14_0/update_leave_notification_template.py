import os

import vmraid
from vmraid import _


def execute():
	base_path = vmraid.get_app_path("erpadda", "hr", "doctype")
	response = vmraid.read_file(
		os.path.join(base_path, "leave_application/leave_application_email_template.html")
	)

	template = vmraid.db.exists("Email Template", _("Leave Approval Notification"))
	if template:
		vmraid.db.set_value("Email Template", template, "response", response)

	template = vmraid.db.exists("Email Template", _("Leave Status Notification"))
	if template:
		vmraid.db.set_value("Email Template", template, "response", response)
