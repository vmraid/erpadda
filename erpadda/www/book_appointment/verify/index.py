import vmraid
from vmraid.utils.verified_command import verify_request


@vmraid.whitelist(allow_guest=True)
def get_context(context):
	if not verify_request():
		context.success = False
		return context

	email = vmraid.form_dict["email"]
	appointment_name = vmraid.form_dict["appointment"]

	if email and appointment_name:
		appointment = vmraid.get_doc("Appointment", appointment_name)
		appointment.set_verified(email)
		context.success = True
		return context
	else:
		context.success = False
		return context
