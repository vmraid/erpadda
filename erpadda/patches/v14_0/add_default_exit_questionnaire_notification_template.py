import os

import vmraid
from vmraid import _


def execute():
	template = vmraid.db.exists("Email Template", _("Exit Questionnaire Notification"))
	if not template:
		base_path = vmraid.get_app_path("erpadda", "hr", "doctype")
		response = vmraid.read_file(
			os.path.join(base_path, "exit_interview/exit_questionnaire_notification_template.html")
		)

		template = vmraid.get_doc(
			{
				"doctype": "Email Template",
				"name": _("Exit Questionnaire Notification"),
				"response": response,
				"subject": _("Exit Questionnaire Notification"),
				"owner": vmraid.session.user,
			}
		).insert(ignore_permissions=True)
		template = template.name

	hr_settings = vmraid.get_doc("HR Settings")
	hr_settings.exit_questionnaire_notification_template = template
	hr_settings.flags.ignore_links = True
	hr_settings.save()
