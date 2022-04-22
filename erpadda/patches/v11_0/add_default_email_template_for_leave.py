import os

import vmraid
from vmraid import _


def execute():
	vmraid.reload_doc("email", "doctype", "email_template")

	if not vmraid.db.exists("Email Template", _("Leave Approval Notification")):
		base_path = vmraid.get_app_path("erpadda", "hr", "doctype")
		response = vmraid.read_file(
			os.path.join(base_path, "leave_application/leave_application_email_template.html")
		)
		vmraid.get_doc(
			{
				"doctype": "Email Template",
				"name": _("Leave Approval Notification"),
				"response": response,
				"subject": _("Leave Approval Notification"),
				"owner": vmraid.session.user,
			}
		).insert(ignore_permissions=True)

	if not vmraid.db.exists("Email Template", _("Leave Status Notification")):
		base_path = vmraid.get_app_path("erpadda", "hr", "doctype")
		response = vmraid.read_file(
			os.path.join(base_path, "leave_application/leave_application_email_template.html")
		)
		vmraid.get_doc(
			{
				"doctype": "Email Template",
				"name": _("Leave Status Notification"),
				"response": response,
				"subject": _("Leave Status Notification"),
				"owner": vmraid.session.user,
			}
		).insert(ignore_permissions=True)
