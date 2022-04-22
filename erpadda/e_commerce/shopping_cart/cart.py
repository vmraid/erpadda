# Copyright (c) 2015, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt

import vmraid
import vmraid.defaults
from vmraid import _, throw
from vmraid.contacts.doctype.address.address import get_address_display
from vmraid.contacts.doctype.contact.contact import get_contact_name
from vmraid.utils import cint, cstr, flt, get_fullname
from vmraid.utils.nestedset import get_root_of

from erpadda.accounts.utils import get_account_name
from erpadda.e_commerce.doctype.e_commerce_settings.e_commerce_settings import (
	get_shopping_cart_settings,
)
from erpadda.utilities.product import get_web_item_qty_in_stock


class WebsitePriceListMissingError(vmraid.ValidationError):
	pass


def set_cart_count(quotation=None):
	if cint(vmraid.db.get_singles_value("E Commerce Settings", "enabled")):
		if not quotation:
			quotation = _get_cart_quotation()
		cart_count = cstr(cint(quotation.get("total_qty")))

		if hasattr(vmraid.local, "cookie_manager"):
			vmraid.local.cookie_manager.set_cookie("cart_count", cart_count)


@vmraid.whitelist()
def get_cart_quotation(doc=None):
	party = get_party()

	if not doc:
		quotation = _get_cart_quotation(party)
		doc = quotation
		set_cart_count(quotation)

	addresses = get_address_docs(party=party)

	if not doc.customer_address and addresses:
		update_cart_address("billing", addresses[0].name)

	return {
		"doc": decorate_quotation_doc(doc),
		"shipping_addresses": get_shipping_addresses(party),
		"billing_addresses": get_billing_addresses(party),
		"shipping_rules": get_applicable_shipping_rules(party),
		"cart_settings": vmraid.get_cached_doc("E Commerce Settings"),
	}


@vmraid.whitelist()
def get_shipping_addresses(party=None):
	if not party:
		party = get_party()
	addresses = get_address_docs(party=party)
	return [
		{"name": address.name, "title": address.address_title, "display": address.display}
		for address in addresses
		if address.address_type == "Shipping"
	]


@vmraid.whitelist()
def get_billing_addresses(party=None):
	if not party:
		party = get_party()
	addresses = get_address_docs(party=party)
	return [
		{"name": address.name, "title": address.address_title, "display": address.display}
		for address in addresses
		if address.address_type == "Billing"
	]


@vmraid.whitelist()
def place_order():
	quotation = _get_cart_quotation()
	cart_settings = vmraid.db.get_value(
		"E Commerce Settings", None, ["company", "allow_items_not_in_stock"], as_dict=1
	)
	quotation.company = cart_settings.company

	quotation.flags.ignore_permissions = True
	quotation.submit()

	if quotation.quotation_to == "Lead" and quotation.party_name:
		# company used to create customer accounts
		vmraid.defaults.set_user_default("company", quotation.company)

	if not (quotation.shipping_address_name or quotation.customer_address):
		vmraid.throw(_("Set Shipping Address or Billing Address"))

	from erpadda.selling.doctype.quotation.quotation import _make_sales_order

	sales_order = vmraid.get_doc(_make_sales_order(quotation.name, ignore_permissions=True))
	sales_order.payment_schedule = []

	if not cint(cart_settings.allow_items_not_in_stock):
		for item in sales_order.get("items"):
			item.warehouse = vmraid.db.get_value(
				"Website Item", {"item_code": item.item_code}, "website_warehouse"
			)
			is_stock_item = vmraid.db.get_value("Item", item.item_code, "is_stock_item")

			if is_stock_item:
				item_stock = get_web_item_qty_in_stock(item.item_code, "website_warehouse")
				if not cint(item_stock.in_stock):
					throw(_("{0} Not in Stock").format(item.item_code))
				if item.qty > item_stock.stock_qty[0][0]:
					throw(_("Only {0} in Stock for item {1}").format(item_stock.stock_qty[0][0], item.item_code))

	sales_order.flags.ignore_permissions = True
	sales_order.insert()
	sales_order.submit()

	if hasattr(vmraid.local, "cookie_manager"):
		vmraid.local.cookie_manager.delete_cookie("cart_count")

	return sales_order.name


@vmraid.whitelist()
def request_for_quotation():
	quotation = _get_cart_quotation()
	quotation.flags.ignore_permissions = True

	if get_shopping_cart_settings().save_quotations_as_draft:
		quotation.save()
	else:
		quotation.submit()
	return quotation.name


@vmraid.whitelist()
def update_cart(item_code, qty, additional_notes=None, with_items=False):
	quotation = _get_cart_quotation()

	empty_card = False
	qty = flt(qty)
	if qty == 0:
		quotation_items = quotation.get("items", {"item_code": ["!=", item_code]})
		if quotation_items:
			quotation.set("items", quotation_items)
		else:
			empty_card = True

	else:
		quotation_items = quotation.get("items", {"item_code": item_code})
		if not quotation_items:
			quotation.append(
				"items",
				{
					"doctype": "Quotation Item",
					"item_code": item_code,
					"qty": qty,
					"additional_notes": additional_notes,
				},
			)
		else:
			quotation_items[0].qty = qty
			quotation_items[0].additional_notes = additional_notes

	apply_cart_settings(quotation=quotation)

	quotation.flags.ignore_permissions = True
	quotation.payment_schedule = []
	if not empty_card:
		quotation.save()
	else:
		quotation.delete()
		quotation = None

	set_cart_count(quotation)

	if cint(with_items):
		context = get_cart_quotation(quotation)
		return {
			"items": vmraid.render_template("templates/includes/cart/cart_items.html", context),
			"total": vmraid.render_template("templates/includes/cart/cart_items_total.html", context),
			"taxes_and_totals": vmraid.render_template(
				"templates/includes/cart/cart_payment_summary.html", context
			),
		}
	else:
		return {"name": quotation.name}


@vmraid.whitelist()
def get_shopping_cart_menu(context=None):
	if not context:
		context = get_cart_quotation()

	return vmraid.render_template("templates/includes/cart/cart_dropdown.html", context)


@vmraid.whitelist()
def add_new_address(doc):
	doc = vmraid.parse_json(doc)
	doc.update({"doctype": "Address"})
	address = vmraid.get_doc(doc)
	address.save(ignore_permissions=True)

	return address


@vmraid.whitelist(allow_guest=True)
def create_lead_for_item_inquiry(lead, subject, message):
	lead = vmraid.parse_json(lead)
	lead_doc = vmraid.new_doc("Lead")
	for fieldname in ("lead_name", "company_name", "email_id", "phone"):
		lead_doc.set(fieldname, lead.get(fieldname))

	lead_doc.set("lead_owner", "")

	if not vmraid.db.exists("Lead Source", "Product Inquiry"):
		vmraid.get_doc({"doctype": "Lead Source", "source_name": "Product Inquiry"}).insert(
			ignore_permissions=True
		)

	lead_doc.set("source", "Product Inquiry")

	try:
		lead_doc.save(ignore_permissions=True)
	except vmraid.exceptions.DuplicateEntryError:
		vmraid.clear_messages()
		lead_doc = vmraid.get_doc("Lead", {"email_id": lead["email_id"]})

	lead_doc.add_comment(
		"Comment",
		text="""
		<div>
			<h5>{subject}</h5>
			<p>{message}</p>
		</div>
	""".format(
			subject=subject, message=message
		),
	)

	return lead_doc


@vmraid.whitelist()
def get_terms_and_conditions(terms_name):
	return vmraid.db.get_value("Terms and Conditions", terms_name, "terms")


@vmraid.whitelist()
def update_cart_address(address_type, address_name):
	quotation = _get_cart_quotation()
	address_doc = vmraid.get_doc("Address", address_name).as_dict()
	address_display = get_address_display(address_doc)

	if address_type.lower() == "billing":
		quotation.customer_address = address_name
		quotation.address_display = address_display
		quotation.shipping_address_name = quotation.shipping_address_name or address_name
		address_doc = next((doc for doc in get_billing_addresses() if doc["name"] == address_name), None)
	elif address_type.lower() == "shipping":
		quotation.shipping_address_name = address_name
		quotation.shipping_address = address_display
		quotation.customer_address = quotation.customer_address or address_name
		address_doc = next(
			(doc for doc in get_shipping_addresses() if doc["name"] == address_name), None
		)
	apply_cart_settings(quotation=quotation)

	quotation.flags.ignore_permissions = True
	quotation.save()

	context = get_cart_quotation(quotation)
	context["address"] = address_doc

	return {
		"taxes": vmraid.render_template("templates/includes/order/order_taxes.html", context),
		"address": vmraid.render_template("templates/includes/cart/address_card.html", context),
	}


def guess_territory():
	territory = None
	geoip_country = vmraid.session.get("session_country")
	if geoip_country:
		territory = vmraid.db.get_value("Territory", geoip_country)

	return (
		territory
		or vmraid.db.get_value("E Commerce Settings", None, "territory")
		or get_root_of("Territory")
	)


def decorate_quotation_doc(doc):
	for d in doc.get("items", []):
		item_code = d.item_code
		fields = ["web_item_name", "thumbnail", "website_image", "description", "route"]

		# Variant Item
		if not vmraid.db.exists("Website Item", {"item_code": item_code}):
			variant_data = vmraid.db.get_values(
				"Item",
				filters={"item_code": item_code},
				fieldname=["variant_of", "item_name", "image"],
				as_dict=True,
			)[0]
			item_code = variant_data.variant_of
			fields = fields[1:]
			d.web_item_name = variant_data.item_name

			if variant_data.image:  # get image from variant or template web item
				d.thumbnail = variant_data.image
				fields = fields[2:]

		d.update(vmraid.db.get_value("Website Item", {"item_code": item_code}, fields, as_dict=True))

	return doc


def _get_cart_quotation(party=None):
	"""Return the open Quotation of type "Shopping Cart" or make a new one"""
	if not party:
		party = get_party()

	quotation = vmraid.get_all(
		"Quotation",
		fields=["name"],
		filters={
			"party_name": party.name,
			"contact_email": vmraid.session.user,
			"order_type": "Shopping Cart",
			"docstatus": 0,
		},
		order_by="modified desc",
		limit_page_length=1,
	)

	if quotation:
		qdoc = vmraid.get_doc("Quotation", quotation[0].name)
	else:
		company = vmraid.db.get_value("E Commerce Settings", None, ["company"])
		qdoc = vmraid.get_doc(
			{
				"doctype": "Quotation",
				"naming_series": get_shopping_cart_settings().quotation_series or "QTN-CART-",
				"quotation_to": party.doctype,
				"company": company,
				"order_type": "Shopping Cart",
				"status": "Draft",
				"docstatus": 0,
				"__islocal": 1,
				"party_name": party.name,
			}
		)

		qdoc.contact_person = vmraid.db.get_value("Contact", {"email_id": vmraid.session.user})
		qdoc.contact_email = vmraid.session.user

		qdoc.flags.ignore_permissions = True
		qdoc.run_method("set_missing_values")
		apply_cart_settings(party, qdoc)

	return qdoc


def update_party(fullname, company_name=None, mobile_no=None, phone=None):
	party = get_party()

	party.customer_name = company_name or fullname
	party.customer_type = "Company" if company_name else "Individual"

	contact_name = vmraid.db.get_value("Contact", {"email_id": vmraid.session.user})
	contact = vmraid.get_doc("Contact", contact_name)
	contact.first_name = fullname
	contact.last_name = None
	contact.customer_name = party.customer_name
	contact.mobile_no = mobile_no
	contact.phone = phone
	contact.flags.ignore_permissions = True
	contact.save()

	party_doc = vmraid.get_doc(party.as_dict())
	party_doc.flags.ignore_permissions = True
	party_doc.save()

	qdoc = _get_cart_quotation(party)
	if not qdoc.get("__islocal"):
		qdoc.customer_name = company_name or fullname
		qdoc.run_method("set_missing_lead_customer_details")
		qdoc.flags.ignore_permissions = True
		qdoc.save()


def apply_cart_settings(party=None, quotation=None):
	if not party:
		party = get_party()
	if not quotation:
		quotation = _get_cart_quotation(party)

	cart_settings = vmraid.get_doc("E Commerce Settings")

	set_price_list_and_rate(quotation, cart_settings)

	quotation.run_method("calculate_taxes_and_totals")

	set_taxes(quotation, cart_settings)

	_apply_shipping_rule(party, quotation, cart_settings)


def set_price_list_and_rate(quotation, cart_settings):
	"""set price list based on billing territory"""

	_set_price_list(cart_settings, quotation)

	# reset values
	quotation.price_list_currency = (
		quotation.currency
	) = quotation.plc_conversion_rate = quotation.conversion_rate = None
	for item in quotation.get("items"):
		item.price_list_rate = item.discount_percentage = item.rate = item.amount = None

	# refetch values
	quotation.run_method("set_price_list_and_item_details")

	if hasattr(vmraid.local, "cookie_manager"):
		# set it in cookies for using in product page
		vmraid.local.cookie_manager.set_cookie("selling_price_list", quotation.selling_price_list)


def _set_price_list(cart_settings, quotation=None):
	"""Set price list based on customer or shopping cart default"""
	from erpadda.accounts.party import get_default_price_list

	party_name = quotation.get("party_name") if quotation else get_party().get("name")
	selling_price_list = None

	# check if default customer price list exists
	if party_name and vmraid.db.exists("Customer", party_name):
		selling_price_list = get_default_price_list(vmraid.get_doc("Customer", party_name))

	# check default price list in shopping cart
	if not selling_price_list:
		selling_price_list = cart_settings.price_list

	if quotation:
		quotation.selling_price_list = selling_price_list

	return selling_price_list


def set_taxes(quotation, cart_settings):
	"""set taxes based on billing territory"""
	from erpadda.accounts.party import set_taxes

	customer_group = vmraid.db.get_value("Customer", quotation.party_name, "customer_group")

	quotation.taxes_and_charges = set_taxes(
		quotation.party_name,
		"Customer",
		quotation.transaction_date,
		quotation.company,
		customer_group=customer_group,
		supplier_group=None,
		tax_category=quotation.tax_category,
		billing_address=quotation.customer_address,
		shipping_address=quotation.shipping_address_name,
		use_for_shopping_cart=1,
	)
	#
	# 	# clear table
	quotation.set("taxes", [])
	#
	# 	# append taxes
	quotation.append_taxes_from_master()


def get_party(user=None):
	if not user:
		user = vmraid.session.user

	contact_name = get_contact_name(user)
	party = None

	if contact_name:
		contact = vmraid.get_doc("Contact", contact_name)
		if contact.links:
			party_doctype = contact.links[0].link_doctype
			party = contact.links[0].link_name

	cart_settings = vmraid.get_doc("E Commerce Settings")

	debtors_account = ""

	if cart_settings.enable_checkout:
		debtors_account = get_debtors_account(cart_settings)

	if party:
		return vmraid.get_doc(party_doctype, party)

	else:
		if not cart_settings.enabled:
			vmraid.local.flags.redirect_location = "/contact"
			raise vmraid.Redirect
		customer = vmraid.new_doc("Customer")
		fullname = get_fullname(user)
		customer.update(
			{
				"customer_name": fullname,
				"customer_type": "Individual",
				"customer_group": get_shopping_cart_settings().default_customer_group,
				"territory": get_root_of("Territory"),
			}
		)

		if debtors_account:
			customer.update({"accounts": [{"company": cart_settings.company, "account": debtors_account}]})

		customer.flags.ignore_mandatory = True
		customer.insert(ignore_permissions=True)

		contact = vmraid.new_doc("Contact")
		contact.update({"first_name": fullname, "email_ids": [{"email_id": user, "is_primary": 1}]})
		contact.append("links", dict(link_doctype="Customer", link_name=customer.name))
		contact.flags.ignore_mandatory = True
		contact.insert(ignore_permissions=True)

		return customer


def get_debtors_account(cart_settings):
	if not cart_settings.payment_gateway_account:
		vmraid.throw(_("Payment Gateway Account not set"), _("Mandatory"))

	payment_gateway_account_currency = vmraid.get_doc(
		"Payment Gateway Account", cart_settings.payment_gateway_account
	).currency

	account_name = _("Debtors ({0})").format(payment_gateway_account_currency)

	debtors_account_name = get_account_name(
		"Receivable",
		"Asset",
		is_group=0,
		account_currency=payment_gateway_account_currency,
		company=cart_settings.company,
	)

	if not debtors_account_name:
		debtors_account = vmraid.get_doc(
			{
				"doctype": "Account",
				"account_type": "Receivable",
				"root_type": "Asset",
				"is_group": 0,
				"parent_account": get_account_name(
					root_type="Asset", is_group=1, company=cart_settings.company
				),
				"account_name": account_name,
				"currency": payment_gateway_account_currency,
			}
		).insert(ignore_permissions=True)

		return debtors_account.name

	else:
		return debtors_account_name


def get_address_docs(
	doctype=None, txt=None, filters=None, limit_start=0, limit_page_length=20, party=None
):
	if not party:
		party = get_party()

	if not party:
		return []

	address_names = vmraid.db.get_all(
		"Dynamic Link",
		fields=("parent"),
		filters=dict(parenttype="Address", link_doctype=party.doctype, link_name=party.name),
	)

	out = []

	for a in address_names:
		address = vmraid.get_doc("Address", a.parent)
		address.display = get_address_display(address.as_dict())
		out.append(address)

	return out


@vmraid.whitelist()
def apply_shipping_rule(shipping_rule):
	quotation = _get_cart_quotation()

	quotation.shipping_rule = shipping_rule

	apply_cart_settings(quotation=quotation)

	quotation.flags.ignore_permissions = True
	quotation.save()

	return get_cart_quotation(quotation)


def _apply_shipping_rule(party=None, quotation=None, cart_settings=None):
	if not quotation.shipping_rule:
		shipping_rules = get_shipping_rules(quotation, cart_settings)

		if not shipping_rules:
			return

		elif quotation.shipping_rule not in shipping_rules:
			quotation.shipping_rule = shipping_rules[0]

	if quotation.shipping_rule:
		quotation.run_method("apply_shipping_rule")
		quotation.run_method("calculate_taxes_and_totals")


def get_applicable_shipping_rules(party=None, quotation=None):
	shipping_rules = get_shipping_rules(quotation)

	if shipping_rules:
		rule_label_map = vmraid.db.get_values("Shipping Rule", shipping_rules, "label")
		# we need this in sorted order as per the position of the rule in the settings page
		return [[rule, rule] for rule in shipping_rules]


def get_shipping_rules(quotation=None, cart_settings=None):
	if not quotation:
		quotation = _get_cart_quotation()

	shipping_rules = []
	if quotation.shipping_address_name:
		country = vmraid.db.get_value("Address", quotation.shipping_address_name, "country")
		if country:
			sr_country = vmraid.qb.DocType("Shipping Rule Country")
			sr = vmraid.qb.DocType("Shipping Rule")
			query = (
				vmraid.qb.from_(sr_country)
				.join(sr)
				.on(sr.name == sr_country.parent)
				.select(sr.name)
				.distinct()
				.where((sr_country.country == country) & (sr.disabled != 1))
			)
			result = query.run(as_list=True)
			shipping_rules = [x[0] for x in result]

	return shipping_rules


def get_address_territory(address_name):
	"""Tries to match city, state and country of address to existing territory"""
	territory = None

	if address_name:
		address_fields = vmraid.db.get_value("Address", address_name, ["city", "state", "country"])
		for value in address_fields:
			territory = vmraid.db.get_value("Territory", value)
			if territory:
				break

	return territory


def show_terms(doc):
	return doc.tc_name


@vmraid.whitelist(allow_guest=True)
def apply_coupon_code(applied_code, applied_referral_sales_partner):
	quotation = True

	if not applied_code:
		vmraid.throw(_("Please enter a coupon code"))

	coupon_list = vmraid.get_all("Coupon Code", filters={"coupon_code": applied_code})
	if not coupon_list:
		vmraid.throw(_("Please enter a valid coupon code"))

	coupon_name = coupon_list[0].name

	from erpadda.accounts.doctype.pricing_rule.utils import validate_coupon_code

	validate_coupon_code(coupon_name)
	quotation = _get_cart_quotation()
	quotation.coupon_code = coupon_name
	quotation.flags.ignore_permissions = True
	quotation.save()

	if applied_referral_sales_partner:
		sales_partner_list = vmraid.get_all(
			"Sales Partner", filters={"referral_code": applied_referral_sales_partner}
		)
		if sales_partner_list:
			sales_partner_name = sales_partner_list[0].name
			quotation.referral_sales_partner = sales_partner_name
			quotation.flags.ignore_permissions = True
			quotation.save()

	return quotation
