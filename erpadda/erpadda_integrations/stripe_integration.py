# Copyright (c) 2018, VMRaid and contributors
# For license information, please see license.txt

import vmraid
import stripe
from vmraid import _
from vmraid.integrations.utils import create_request_log


def create_stripe_subscription(gateway_controller, data):
	stripe_settings = vmraid.get_doc("Stripe Settings", gateway_controller)
	stripe_settings.data = vmraid._dict(data)

	stripe.api_key = stripe_settings.get_password(fieldname="secret_key", raise_exception=False)
	stripe.default_http_client = stripe.http_client.RequestsClient()

	try:
		stripe_settings.integration_request = create_request_log(stripe_settings.data, "Host", "Stripe")
		stripe_settings.payment_plans = vmraid.get_doc(
			"Payment Request", stripe_settings.data.reference_docname
		).subscription_plans
		return create_subscription_on_stripe(stripe_settings)

	except Exception:
		vmraid.log_error(vmraid.get_traceback())
		return {
			"redirect_to": vmraid.redirect_to_message(
				_("Server Error"),
				_(
					"It seems that there is an issue with the server's stripe configuration. In case of failure, the amount will get refunded to your account."
				),
			),
			"status": 401,
		}


def create_subscription_on_stripe(stripe_settings):
	items = []
	for payment_plan in stripe_settings.payment_plans:
		plan = vmraid.db.get_value("Subscription Plan", payment_plan.plan, "product_price_id")
		items.append({"price": plan, "quantity": payment_plan.qty})

	try:
		customer = stripe.Customer.create(
			source=stripe_settings.data.stripe_token_id,
			description=stripe_settings.data.payer_name,
			email=stripe_settings.data.payer_email,
		)

		subscription = stripe.Subscription.create(customer=customer, items=items)

		if subscription.status == "active":
			stripe_settings.integration_request.db_set("status", "Completed", update_modified=False)
			stripe_settings.flags.status_changed_to = "Completed"

		else:
			stripe_settings.integration_request.db_set("status", "Failed", update_modified=False)
			vmraid.log_error("Subscription N°: " + subscription.id, "Stripe Payment not completed")
	except Exception:
		stripe_settings.integration_request.db_set("status", "Failed", update_modified=False)
		vmraid.log_error(vmraid.get_traceback())

	return stripe_settings.finalize_request()
