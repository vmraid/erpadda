import base64
import hashlib
import hmac
import json

import vmraid
from vmraid import _
from vmraid.utils import cstr


def verify_request():
	woocommerce_settings = vmraid.get_doc("Woocommerce Settings")
	sig = base64.b64encode(
		hmac.new(
			woocommerce_settings.secret.encode("utf8"), vmraid.request.data, hashlib.sha256
		).digest()
	)

	if (
		vmraid.request.data
		and not sig == vmraid.get_request_header("X-Wc-Webhook-Signature", "").encode()
	):
		vmraid.throw(_("Unverified Webhook Data"))
	vmraid.set_user(woocommerce_settings.creation_user)


@vmraid.whitelist(allow_guest=True)
def order(*args, **kwargs):
	try:
		_order(*args, **kwargs)
	except Exception:
		error_message = (
			vmraid.get_traceback() + "\n\n Request Data: \n" + json.loads(vmraid.request.data).__str__()
		)
		vmraid.log_error(error_message, "WooCommerce Error")
		raise


def _order(*args, **kwargs):
	woocommerce_settings = vmraid.get_doc("Woocommerce Settings")
	if vmraid.flags.woocomm_test_order_data:
		order = vmraid.flags.woocomm_test_order_data
		event = "created"

	elif vmraid.request and vmraid.request.data:
		verify_request()
		try:
			order = json.loads(vmraid.request.data)
		except ValueError:
			# woocommerce returns 'webhook_id=value' for the first request which is not JSON
			order = vmraid.request.data
		event = vmraid.get_request_header("X-Wc-Webhook-Event")

	else:
		return "success"

	if event == "created":
		sys_lang = vmraid.get_single("System Settings").language or "en"
		raw_billing_data = order.get("billing")
		raw_shipping_data = order.get("shipping")
		customer_name = raw_billing_data.get("first_name") + " " + raw_billing_data.get("last_name")
		link_customer_and_address(raw_billing_data, raw_shipping_data, customer_name)
		link_items(order.get("line_items"), woocommerce_settings, sys_lang)
		create_sales_order(order, woocommerce_settings, customer_name, sys_lang)


def link_customer_and_address(raw_billing_data, raw_shipping_data, customer_name):
	customer_woo_com_email = raw_billing_data.get("email")
	customer_exists = vmraid.get_value("Customer", {"woocommerce_email": customer_woo_com_email})
	if not customer_exists:
		# Create Customer
		customer = vmraid.new_doc("Customer")
	else:
		# Edit Customer
		customer = vmraid.get_doc("Customer", {"woocommerce_email": customer_woo_com_email})
		old_name = customer.customer_name

	customer.customer_name = customer_name
	customer.woocommerce_email = customer_woo_com_email
	customer.flags.ignore_mandatory = True
	customer.save()

	if customer_exists:
		vmraid.rename_doc("Customer", old_name, customer_name)
		for address_type in (
			"Billing",
			"Shipping",
		):
			try:
				address = vmraid.get_doc(
					"Address", {"woocommerce_email": customer_woo_com_email, "address_type": address_type}
				)
				rename_address(address, customer)
			except (
				vmraid.DoesNotExistError,
				vmraid.DuplicateEntryError,
				vmraid.ValidationError,
			):
				pass
	else:
		create_address(raw_billing_data, customer, "Billing")
		create_address(raw_shipping_data, customer, "Shipping")
		create_contact(raw_billing_data, customer)


def create_contact(data, customer):
	email = data.get("email", None)
	phone = data.get("phone", None)

	if not email and not phone:
		return

	contact = vmraid.new_doc("Contact")
	contact.first_name = data.get("first_name")
	contact.last_name = data.get("last_name")
	contact.is_primary_contact = 1
	contact.is_billing_contact = 1

	if phone:
		contact.add_phone(phone, is_primary_mobile_no=1, is_primary_phone=1)

	if email:
		contact.add_email(email, is_primary=1)

	contact.append("links", {"link_doctype": "Customer", "link_name": customer.name})

	contact.flags.ignore_mandatory = True
	contact.save()


def create_address(raw_data, customer, address_type):
	address = vmraid.new_doc("Address")

	address.address_line1 = raw_data.get("address_1", "Not Provided")
	address.address_line2 = raw_data.get("address_2", "Not Provided")
	address.city = raw_data.get("city", "Not Provided")
	address.woocommerce_email = customer.woocommerce_email
	address.address_type = address_type
	address.country = vmraid.get_value("Country", {"code": raw_data.get("country", "IN").lower()})
	address.state = raw_data.get("state")
	address.pincode = raw_data.get("postcode")
	address.phone = raw_data.get("phone")
	address.email_id = customer.woocommerce_email
	address.append("links", {"link_doctype": "Customer", "link_name": customer.name})

	address.flags.ignore_mandatory = True
	address.save()


def rename_address(address, customer):
	old_address_title = address.name
	new_address_title = customer.name + "-" + address.address_type
	address.address_title = customer.customer_name
	address.save()

	vmraid.rename_doc("Address", old_address_title, new_address_title)


def link_items(items_list, woocommerce_settings, sys_lang):
	for item_data in items_list:
		item_woo_com_id = cstr(item_data.get("product_id"))

		if not vmraid.db.get_value("Item", {"woocommerce_id": item_woo_com_id}, "name"):
			# Create Item
			item = vmraid.new_doc("Item")
			item.item_code = _("woocommerce - {0}", sys_lang).format(item_woo_com_id)
			item.stock_uom = woocommerce_settings.uom or _("Nos", sys_lang)
			item.item_group = _("WooCommerce Products", sys_lang)

			item.item_name = item_data.get("name")
			item.woocommerce_id = item_woo_com_id
			item.flags.ignore_mandatory = True
			item.save()


def create_sales_order(order, woocommerce_settings, customer_name, sys_lang):
	new_sales_order = vmraid.new_doc("Sales Order")
	new_sales_order.customer = customer_name

	new_sales_order.po_no = new_sales_order.woocommerce_id = order.get("id")
	new_sales_order.naming_series = woocommerce_settings.sales_order_series or "SO-WOO-"

	created_date = order.get("date_created").split("T")
	new_sales_order.transaction_date = created_date[0]
	delivery_after = woocommerce_settings.delivery_after_days or 7
	new_sales_order.delivery_date = vmraid.utils.add_days(created_date[0], delivery_after)

	new_sales_order.company = woocommerce_settings.company

	set_items_in_sales_order(new_sales_order, woocommerce_settings, order, sys_lang)
	new_sales_order.flags.ignore_mandatory = True
	new_sales_order.insert()
	new_sales_order.submit()

	vmraid.db.commit()


def set_items_in_sales_order(new_sales_order, woocommerce_settings, order, sys_lang):
	company_abbr = vmraid.db.get_value("Company", woocommerce_settings.company, "abbr")

	default_warehouse = _("Stores - {0}", sys_lang).format(company_abbr)
	if not vmraid.db.exists("Warehouse", default_warehouse) and not woocommerce_settings.warehouse:
		vmraid.throw(_("Please set Warehouse in Woocommerce Settings"))

	for item in order.get("line_items"):
		woocomm_item_id = item.get("product_id")
		found_item = vmraid.get_doc("Item", {"woocommerce_id": cstr(woocomm_item_id)})

		ordered_items_tax = item.get("total_tax")

		new_sales_order.append(
			"items",
			{
				"item_code": found_item.name,
				"item_name": found_item.item_name,
				"description": found_item.item_name,
				"delivery_date": new_sales_order.delivery_date,
				"uom": woocommerce_settings.uom or _("Nos", sys_lang),
				"qty": item.get("quantity"),
				"rate": item.get("price"),
				"warehouse": woocommerce_settings.warehouse or default_warehouse,
			},
		)

		add_tax_details(
			new_sales_order, ordered_items_tax, "Ordered Item tax", woocommerce_settings.tax_account
		)

	# shipping_details = order.get("shipping_lines") # used for detailed order

	add_tax_details(
		new_sales_order, order.get("shipping_tax"), "Shipping Tax", woocommerce_settings.f_n_f_account
	)
	add_tax_details(
		new_sales_order,
		order.get("shipping_total"),
		"Shipping Total",
		woocommerce_settings.f_n_f_account,
	)


def add_tax_details(sales_order, price, desc, tax_account_head):
	sales_order.append(
		"taxes",
		{
			"charge_type": "Actual",
			"account_head": tax_account_head,
			"tax_amount": price,
			"description": desc,
		},
	)
