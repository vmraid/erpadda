# Copyright (c) 2019, VMRaid and contributors
# For license information, please see license.txt


import vmraid
from vmraid.model.document import Document


class AppointmentLetter(Document):
	pass


@vmraid.whitelist()
def get_appointment_letter_details(template):
	body = []
	intro = vmraid.get_list(
		"Appointment Letter Template",
		fields=["introduction", "closing_notes"],
		filters={"name": template},
	)[0]
	content = vmraid.get_all(
		"Appointment Letter content",
		fields=["title", "description"],
		filters={"parent": template},
		order_by="idx",
	)
	body.append(intro)
	body.append({"description": content})
	return body
