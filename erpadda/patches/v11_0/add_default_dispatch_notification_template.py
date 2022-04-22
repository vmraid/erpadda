import os

import vmraid
from vmraid import _


def execute():
	vmraid.reload_doc("email", "doctype", "email_template")
	vmraid.reload_doc("stock", "doctype", "delivery_settings")

	if not vmraid.db.exists("Email Template", _("Dispatch Notification")):
		base_path = vmraid.get_app_path("erpadda", "stock", "doctype")
		response = vmraid.read_file(
			os.path.join(base_path, "delivery_trip/dispatch_notification_template.html")
		)

		vmraid.get_doc(
			{
				"doctype": "Email Template",
				"name": _("Dispatch Notification"),
				"response": response,
				"subject": _("Your order is out for delivery!"),
				"owner": vmraid.session.user,
			}
		).insert(ignore_permissions=True)

	delivery_settings = vmraid.get_doc("Delivery Settings")
	delivery_settings.dispatch_template = _("Dispatch Notification")
	delivery_settings.flags.ignore_links = True
	delivery_settings.save()
