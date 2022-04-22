# Copyright (c) 2018, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt

import vmraid
from vmraid import _

from erpadda.erpadda_integrations.doctype.gocardless_settings.gocardless_settings import (
	get_gateway_controller,
	gocardless_initialization,
)

no_cache = 1

expected_keys = ("redirect_flow_id", "reference_doctype", "reference_docname")


def get_context(context):
	context.no_cache = 1

	# all these keys exist in form_dict
	if not (set(expected_keys) - set(vmraid.form_dict.keys())):
		for key in expected_keys:
			context[key] = vmraid.form_dict[key]

	else:
		vmraid.redirect_to_message(
			_("Some information is missing"),
			_("Looks like someone sent you to an incomplete URL. Please ask them to look into it."),
		)
		vmraid.local.flags.redirect_location = vmraid.local.response.location
		raise vmraid.Redirect


@vmraid.whitelist(allow_guest=True)
def confirm_payment(redirect_flow_id, reference_doctype, reference_docname):

	client = gocardless_initialization(reference_docname)

	try:
		redirect_flow = client.redirect_flows.complete(
			redirect_flow_id, params={"session_token": vmraid.session.user}
		)

		confirmation_url = redirect_flow.confirmation_url
		gocardless_success_page = vmraid.get_hooks("gocardless_success_page")
		if gocardless_success_page:
			confirmation_url = vmraid.get_attr(gocardless_success_page[-1])(
				reference_doctype, reference_docname
			)

		data = {
			"mandate": redirect_flow.links.mandate,
			"customer": redirect_flow.links.customer,
			"redirect_to": confirmation_url,
			"redirect_message": "Mandate successfully created",
			"reference_doctype": reference_doctype,
			"reference_docname": reference_docname,
		}

		try:
			create_mandate(data)
		except Exception as e:
			vmraid.log_error(e, "GoCardless Mandate Registration Error")

		gateway_controller = get_gateway_controller(reference_docname)
		vmraid.get_doc("GoCardless Settings", gateway_controller).create_payment_request(data)

		return {"redirect_to": confirmation_url}

	except Exception as e:
		vmraid.log_error(e, "GoCardless Payment Error")
		return {"redirect_to": "/integrations/payment-failed"}


def create_mandate(data):
	data = vmraid._dict(data)
	vmraid.logger().debug(data)

	mandate = data.get("mandate")

	if vmraid.db.exists("GoCardless Mandate", mandate):
		return

	else:
		reference_doc = vmraid.db.get_value(
			data.get("reference_doctype"),
			data.get("reference_docname"),
			["reference_doctype", "reference_name"],
			as_dict=1,
		)
		erpadda_customer = vmraid.db.get_value(
			reference_doc.reference_doctype, reference_doc.reference_name, ["customer_name"], as_dict=1
		)

		try:
			vmraid.get_doc(
				{
					"doctype": "GoCardless Mandate",
					"mandate": mandate,
					"customer": erpadda_customer.customer_name,
					"gocardless_customer": data.get("customer"),
				}
			).insert(ignore_permissions=True)

		except Exception:
			vmraid.log_error(vmraid.get_traceback())
