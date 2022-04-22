# Copyright (c) 2015, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid
from vmraid import _, msgprint, scrub
from vmraid.contacts.doctype.address.address import (
	get_address_display,
	get_company_address,
	get_default_address,
)
from vmraid.contacts.doctype.contact.contact import get_contact_details
from vmraid.core.doctype.user_permission.user_permission import get_permitted_documents
from vmraid.model.utils import get_fetch_values
from vmraid.utils import (
	add_days,
	add_months,
	add_years,
	cint,
	cstr,
	date_diff,
	flt,
	formatdate,
	get_last_day,
	get_timestamp,
	getdate,
	nowdate,
)

import erpadda
from erpadda import get_company_currency
from erpadda.accounts.utils import get_fiscal_year
from erpadda.exceptions import InvalidAccountCurrency, PartyDisabled, PartyFrozen


class DuplicatePartyAccountError(vmraid.ValidationError):
	pass


@vmraid.whitelist()
def get_party_details(
	party=None,
	account=None,
	party_type="Customer",
	company=None,
	posting_date=None,
	bill_date=None,
	price_list=None,
	currency=None,
	doctype=None,
	ignore_permissions=False,
	fetch_payment_terms_template=True,
	party_address=None,
	company_address=None,
	shipping_address=None,
	pos_profile=None,
):

	if not party:
		return {}
	if not vmraid.db.exists(party_type, party):
		vmraid.throw(_("{0}: {1} does not exists").format(party_type, party))
	return _get_party_details(
		party,
		account,
		party_type,
		company,
		posting_date,
		bill_date,
		price_list,
		currency,
		doctype,
		ignore_permissions,
		fetch_payment_terms_template,
		party_address,
		company_address,
		shipping_address,
		pos_profile,
	)


def _get_party_details(
	party=None,
	account=None,
	party_type="Customer",
	company=None,
	posting_date=None,
	bill_date=None,
	price_list=None,
	currency=None,
	doctype=None,
	ignore_permissions=False,
	fetch_payment_terms_template=True,
	party_address=None,
	company_address=None,
	shipping_address=None,
	pos_profile=None,
):
	party_details = vmraid._dict(
		set_account_and_due_date(party, account, party_type, company, posting_date, bill_date, doctype)
	)
	party = party_details[party_type.lower()]

	if not ignore_permissions and not (
		vmraid.has_permission(party_type, "read", party)
		or vmraid.has_permission(party_type, "select", party)
	):
		vmraid.throw(_("Not permitted for {0}").format(party), vmraid.PermissionError)

	party = vmraid.get_doc(party_type, party)
	currency = party.get("default_currency") or currency or get_company_currency(company)

	party_address, shipping_address = set_address_details(
		party_details,
		party,
		party_type,
		doctype,
		company,
		party_address,
		company_address,
		shipping_address,
	)
	set_contact_details(party_details, party, party_type)
	set_other_values(party_details, party, party_type)
	set_price_list(party_details, party, party_type, price_list, pos_profile)

	party_details["tax_category"] = get_address_tax_category(
		party.get("tax_category"),
		party_address,
		shipping_address if party_type != "Supplier" else party_address,
	)

	tax_template = set_taxes(
		party.name,
		party_type,
		posting_date,
		company,
		customer_group=party_details.customer_group,
		supplier_group=party_details.supplier_group,
		tax_category=party_details.tax_category,
		billing_address=party_address,
		shipping_address=shipping_address,
	)

	if tax_template:
		party_details["taxes_and_charges"] = tax_template

	if cint(fetch_payment_terms_template):
		party_details["payment_terms_template"] = get_payment_terms_template(
			party.name, party_type, company
		)

	if not party_details.get("currency"):
		party_details["currency"] = currency

	# sales team
	if party_type == "Customer":
		party_details["sales_team"] = [
			{
				"sales_person": d.sales_person,
				"allocated_percentage": d.allocated_percentage or None,
				"commission_rate": d.commission_rate,
			}
			for d in party.get("sales_team")
		]

	# supplier tax withholding category
	if party_type == "Supplier" and party:
		party_details["supplier_tds"] = vmraid.get_value(
			party_type, party.name, "tax_withholding_category"
		)

	return party_details


def set_address_details(
	party_details,
	party,
	party_type,
	doctype=None,
	company=None,
	party_address=None,
	company_address=None,
	shipping_address=None,
):
	billing_address_field = (
		"customer_address" if party_type == "Lead" else party_type.lower() + "_address"
	)
	party_details[billing_address_field] = party_address or get_default_address(
		party_type, party.name
	)
	if doctype:
		party_details.update(
			get_fetch_values(doctype, billing_address_field, party_details[billing_address_field])
		)
	# address display
	party_details.address_display = get_address_display(party_details[billing_address_field])
	# shipping address
	if party_type in ["Customer", "Lead"]:
		party_details.shipping_address_name = shipping_address or get_party_shipping_address(
			party_type, party.name
		)
		party_details.shipping_address = get_address_display(party_details["shipping_address_name"])
		if doctype:
			party_details.update(
				get_fetch_values(doctype, "shipping_address_name", party_details.shipping_address_name)
			)

	if company_address:
		party_details.update({"company_address": company_address})
	else:
		party_details.update(get_company_address(company))

	if doctype and doctype in ["Delivery Note", "Sales Invoice", "Sales Order"]:
		if party_details.company_address:
			party_details.update(
				get_fetch_values(doctype, "company_address", party_details.company_address)
			)
		get_regional_address_details(party_details, doctype, company)

	elif doctype and doctype in ["Purchase Invoice", "Purchase Order", "Purchase Receipt"]:
		if party_details.company_address:
			party_details["shipping_address"] = shipping_address or party_details["company_address"]
			party_details.shipping_address_display = get_address_display(party_details["shipping_address"])
			party_details.update(
				get_fetch_values(doctype, "shipping_address", party_details.shipping_address)
			)
		get_regional_address_details(party_details, doctype, company)

	return party_details.get(billing_address_field), party_details.shipping_address_name


@erpadda.allow_regional
def get_regional_address_details(party_details, doctype, company):
	pass


def set_contact_details(party_details, party, party_type):
	party_details.contact_person = get_default_contact(party_type, party.name)

	if not party_details.contact_person:
		party_details.update(
			{
				"contact_person": None,
				"contact_display": None,
				"contact_email": None,
				"contact_mobile": None,
				"contact_phone": None,
				"contact_designation": None,
				"contact_department": None,
			}
		)
	else:
		party_details.update(get_contact_details(party_details.contact_person))


def set_other_values(party_details, party, party_type):
	# copy
	if party_type == "Customer":
		to_copy = ["customer_name", "customer_group", "territory", "language"]
	else:
		to_copy = ["supplier_name", "supplier_group", "language"]
	for f in to_copy:
		party_details[f] = party.get(f)

	# fields prepended with default in Customer doctype
	for f in ["currency"] + (
		["sales_partner", "commission_rate"] if party_type == "Customer" else []
	):
		if party.get("default_" + f):
			party_details[f] = party.get("default_" + f)


def get_default_price_list(party):
	"""Return default price list for party (Document object)"""
	if party.get("default_price_list"):
		return party.default_price_list

	if party.doctype == "Customer":
		return vmraid.db.get_value("Customer Group", party.customer_group, "default_price_list")


def set_price_list(party_details, party, party_type, given_price_list, pos=None):
	# price list
	price_list = get_permitted_documents("Price List")

	# if there is only one permitted document based on user permissions, set it
	if price_list and len(price_list) == 1:
		price_list = price_list[0]
	elif pos and party_type == "Customer":
		customer_price_list = vmraid.get_value("Customer", party.name, "default_price_list")

		if customer_price_list:
			price_list = customer_price_list
		else:
			pos_price_list = vmraid.get_value("POS Profile", pos, "selling_price_list")
			price_list = pos_price_list or given_price_list
	else:
		price_list = get_default_price_list(party) or given_price_list

	if price_list:
		party_details.price_list_currency = vmraid.db.get_value(
			"Price List", price_list, "currency", cache=True
		)

	party_details[
		"selling_price_list" if party.doctype == "Customer" else "buying_price_list"
	] = price_list


def set_account_and_due_date(
	party, account, party_type, company, posting_date, bill_date, doctype
):
	if doctype not in ["POS Invoice", "Sales Invoice", "Purchase Invoice"]:
		# not an invoice
		return {party_type.lower(): party}

	if party:
		account = get_party_account(party_type, party, company)

	account_fieldname = "debit_to" if party_type == "Customer" else "credit_to"
	out = {
		party_type.lower(): party,
		account_fieldname: account,
		"due_date": get_due_date(posting_date, party_type, party, company, bill_date),
	}

	return out


@vmraid.whitelist()
def get_party_account(party_type, party=None, company=None):
	"""Returns the account for the given `party`.
	Will first search in party (Customer / Supplier) record, if not found,
	will search in group (Customer Group / Supplier Group),
	finally will return default."""
	if not company:
		vmraid.throw(_("Please select a Company"))

	if not party and party_type in ["Customer", "Supplier"]:
		default_account_name = (
			"default_receivable_account" if party_type == "Customer" else "default_payable_account"
		)

		return vmraid.get_cached_value("Company", company, default_account_name)

	account = vmraid.db.get_value(
		"Party Account", {"parenttype": party_type, "parent": party, "company": company}, "account"
	)

	if not account and party_type in ["Customer", "Supplier"]:
		party_group_doctype = "Customer Group" if party_type == "Customer" else "Supplier Group"
		group = vmraid.get_cached_value(party_type, party, scrub(party_group_doctype))
		account = vmraid.db.get_value(
			"Party Account",
			{"parenttype": party_group_doctype, "parent": group, "company": company},
			"account",
		)

	if not account and party_type in ["Customer", "Supplier"]:
		default_account_name = (
			"default_receivable_account" if party_type == "Customer" else "default_payable_account"
		)
		account = vmraid.get_cached_value("Company", company, default_account_name)

	existing_gle_currency = get_party_gle_currency(party_type, party, company)
	if existing_gle_currency:
		if account:
			account_currency = vmraid.db.get_value("Account", account, "account_currency", cache=True)
		if (account and account_currency != existing_gle_currency) or not account:
			account = get_party_gle_account(party_type, party, company)

	return account


@vmraid.whitelist()
def get_party_bank_account(party_type, party):
	return vmraid.db.get_value(
		"Bank Account", {"party_type": party_type, "party": party, "is_default": 1}
	)


def get_party_account_currency(party_type, party, company):
	def generator():
		party_account = get_party_account(party_type, party, company)
		return vmraid.db.get_value("Account", party_account, "account_currency", cache=True)

	return vmraid.local_cache("party_account_currency", (party_type, party, company), generator)


def get_party_gle_currency(party_type, party, company):
	def generator():
		existing_gle_currency = vmraid.db.sql(
			"""select account_currency from `tabGL Entry`
			where docstatus=1 and company=%(company)s and party_type=%(party_type)s and party=%(party)s
			limit 1""",
			{"company": company, "party_type": party_type, "party": party},
		)

		return existing_gle_currency[0][0] if existing_gle_currency else None

	return vmraid.local_cache(
		"party_gle_currency", (party_type, party, company), generator, regenerate_if_none=True
	)


def get_party_gle_account(party_type, party, company):
	def generator():
		existing_gle_account = vmraid.db.sql(
			"""select account from `tabGL Entry`
			where docstatus=1 and company=%(company)s and party_type=%(party_type)s and party=%(party)s
			limit 1""",
			{"company": company, "party_type": party_type, "party": party},
		)

		return existing_gle_account[0][0] if existing_gle_account else None

	return vmraid.local_cache(
		"party_gle_account", (party_type, party, company), generator, regenerate_if_none=True
	)


def validate_party_gle_currency(party_type, party, company, party_account_currency=None):
	"""Validate party account currency with existing GL Entry's currency"""
	if not party_account_currency:
		party_account_currency = get_party_account_currency(party_type, party, company)

	existing_gle_currency = get_party_gle_currency(party_type, party, company)

	if existing_gle_currency and party_account_currency != existing_gle_currency:
		vmraid.throw(
			_(
				"{0} {1} has accounting entries in currency {2} for company {3}. Please select a receivable or payable account with currency {2}."
			).format(
				vmraid.bold(party_type),
				vmraid.bold(party),
				vmraid.bold(existing_gle_currency),
				vmraid.bold(company),
			),
			InvalidAccountCurrency,
		)


def validate_party_accounts(doc):
	from erpadda.controllers.accounts_controller import validate_account_head

	companies = []

	for account in doc.get("accounts"):
		if account.company in companies:
			vmraid.throw(
				_("There can only be 1 Account per Company in {0} {1}").format(doc.doctype, doc.name),
				DuplicatePartyAccountError,
			)
		else:
			companies.append(account.company)

		party_account_currency = vmraid.db.get_value(
			"Account", account.account, "account_currency", cache=True
		)
		if vmraid.db.get_default("Company"):
			company_default_currency = vmraid.get_cached_value(
				"Company", vmraid.db.get_default("Company"), "default_currency"
			)
		else:
			company_default_currency = vmraid.db.get_value("Company", account.company, "default_currency")

		validate_party_gle_currency(doc.doctype, doc.name, account.company, party_account_currency)

		if doc.get("default_currency") and party_account_currency and company_default_currency:
			if (
				doc.default_currency != party_account_currency
				and doc.default_currency != company_default_currency
			):
				vmraid.throw(
					_(
						"Billing currency must be equal to either default company's currency or party account currency"
					)
				)

		# validate if account is mapped for same company
		validate_account_head(account.idx, account.account, account.company)


@vmraid.whitelist()
def get_due_date(posting_date, party_type, party, company=None, bill_date=None):
	"""Get due date from `Payment Terms Template`"""
	due_date = None
	if (bill_date or posting_date) and party:
		due_date = bill_date or posting_date
		template_name = get_payment_terms_template(party, party_type, company)

		if template_name:
			due_date = get_due_date_from_template(template_name, posting_date, bill_date).strftime(
				"%Y-%m-%d"
			)
		else:
			if party_type == "Supplier":
				supplier_group = vmraid.get_cached_value(party_type, party, "supplier_group")
				template_name = vmraid.get_cached_value("Supplier Group", supplier_group, "payment_terms")
				if template_name:
					due_date = get_due_date_from_template(template_name, posting_date, bill_date).strftime(
						"%Y-%m-%d"
					)
	# If due date is calculated from bill_date, check this condition
	if getdate(due_date) < getdate(posting_date):
		due_date = posting_date
	return due_date


def get_due_date_from_template(template_name, posting_date, bill_date):
	"""
	Inspects all `Payment Term`s from the a `Payment Terms Template` and returns the due
	date after considering all the `Payment Term`s requirements.
	:param template_name: Name of the `Payment Terms Template`
	:return: String representing the calculated due date
	"""
	due_date = getdate(bill_date or posting_date)

	template = vmraid.get_doc("Payment Terms Template", template_name)

	for term in template.terms:
		if term.due_date_based_on == "Day(s) after invoice date":
			due_date = max(due_date, add_days(due_date, term.credit_days))
		elif term.due_date_based_on == "Day(s) after the end of the invoice month":
			due_date = max(due_date, add_days(get_last_day(due_date), term.credit_days))
		else:
			due_date = max(due_date, add_months(get_last_day(due_date), term.credit_months))
	return due_date


def validate_due_date(
	posting_date, due_date, party_type, party, company=None, bill_date=None, template_name=None
):
	if getdate(due_date) < getdate(posting_date):
		vmraid.throw(_("Due Date cannot be before Posting / Supplier Invoice Date"))
	else:
		if not template_name:
			return

		default_due_date = get_due_date_from_template(template_name, posting_date, bill_date).strftime(
			"%Y-%m-%d"
		)

		if not default_due_date:
			return

		if default_due_date != posting_date and getdate(due_date) > getdate(default_due_date):
			is_credit_controller = (
				vmraid.db.get_single_value("Accounts Settings", "credit_controller") in vmraid.get_roles()
			)
			if is_credit_controller:
				msgprint(
					_("Note: Due / Reference Date exceeds allowed customer credit days by {0} day(s)").format(
						date_diff(due_date, default_due_date)
					)
				)
			else:
				vmraid.throw(
					_("Due / Reference Date cannot be after {0}").format(formatdate(default_due_date))
				)


@vmraid.whitelist()
def get_address_tax_category(tax_category=None, billing_address=None, shipping_address=None):
	addr_tax_category_from = vmraid.db.get_single_value(
		"Accounts Settings", "determine_address_tax_category_from"
	)
	if addr_tax_category_from == "Shipping Address":
		if shipping_address:
			tax_category = vmraid.db.get_value("Address", shipping_address, "tax_category") or tax_category
	else:
		if billing_address:
			tax_category = vmraid.db.get_value("Address", billing_address, "tax_category") or tax_category

	return cstr(tax_category)


@vmraid.whitelist()
def set_taxes(
	party,
	party_type,
	posting_date,
	company,
	customer_group=None,
	supplier_group=None,
	tax_category=None,
	billing_address=None,
	shipping_address=None,
	use_for_shopping_cart=None,
):
	from erpadda.accounts.doctype.tax_rule.tax_rule import get_party_details, get_tax_template

	args = {party_type.lower(): party, "company": company}

	if tax_category:
		args["tax_category"] = tax_category

	if customer_group:
		args["customer_group"] = customer_group

	if supplier_group:
		args["supplier_group"] = supplier_group

	if billing_address or shipping_address:
		args.update(
			get_party_details(
				party, party_type, {"billing_address": billing_address, "shipping_address": shipping_address}
			)
		)
	else:
		args.update(get_party_details(party, party_type))

	if party_type in ("Customer", "Lead"):
		args.update({"tax_type": "Sales"})

		if party_type == "Lead":
			args["customer"] = None
			del args["lead"]
	else:
		args.update({"tax_type": "Purchase"})

	if use_for_shopping_cart:
		args.update({"use_for_shopping_cart": use_for_shopping_cart})

	return get_tax_template(posting_date, args)


@vmraid.whitelist()
def get_payment_terms_template(party_name, party_type, company=None):
	if party_type not in ("Customer", "Supplier"):
		return
	template = None
	if party_type == "Customer":
		customer = vmraid.get_cached_value(
			"Customer", party_name, fieldname=["payment_terms", "customer_group"], as_dict=1
		)
		template = customer.payment_terms

		if not template and customer.customer_group:
			template = vmraid.get_cached_value("Customer Group", customer.customer_group, "payment_terms")
	else:
		supplier = vmraid.get_cached_value(
			"Supplier", party_name, fieldname=["payment_terms", "supplier_group"], as_dict=1
		)
		template = supplier.payment_terms
		if not template and supplier.supplier_group:
			template = vmraid.get_cached_value("Supplier Group", supplier.supplier_group, "payment_terms")

	if not template and company:
		template = vmraid.get_cached_value("Company", company, fieldname="payment_terms")
	return template


def validate_party_frozen_disabled(party_type, party_name):

	if vmraid.flags.ignore_party_validation:
		return

	if party_type and party_name:
		if party_type in ("Customer", "Supplier"):
			party = vmraid.get_cached_value(party_type, party_name, ["is_frozen", "disabled"], as_dict=True)
			if party.disabled:
				vmraid.throw(_("{0} {1} is disabled").format(party_type, party_name), PartyDisabled)
			elif party.get("is_frozen"):
				frozen_accounts_modifier = vmraid.db.get_single_value(
					"Accounts Settings", "frozen_accounts_modifier"
				)
				if not frozen_accounts_modifier in vmraid.get_roles():
					vmraid.throw(_("{0} {1} is frozen").format(party_type, party_name), PartyFrozen)

		elif party_type == "Employee":
			if vmraid.db.get_value("Employee", party_name, "status") != "Active":
				vmraid.msgprint(_("{0} {1} is not active").format(party_type, party_name), alert=True)


def get_timeline_data(doctype, name):
	"""returns timeline data for the past one year"""
	from vmraid.desk.form.load import get_communication_data

	out = {}
	fields = "creation, count(*)"
	after = add_years(None, -1).strftime("%Y-%m-%d")
	group_by = "group by Date(creation)"

	data = get_communication_data(
		doctype,
		name,
		after=after,
		group_by="group by creation",
		fields="C.creation as creation, count(C.name)",
		as_dict=False,
	)

	# fetch and append data from Activity Log
	data += vmraid.db.sql(
		"""select {fields}
		from `tabActivity Log`
		where (reference_doctype=%(doctype)s and reference_name=%(name)s)
		or (timeline_doctype in (%(doctype)s) and timeline_name=%(name)s)
		or (reference_doctype in ("Quotation", "Opportunity") and timeline_name=%(name)s)
		and status!='Success' and creation > {after}
		{group_by} order by creation desc
		""".format(
			fields=fields, group_by=group_by, after=after
		),
		{"doctype": doctype, "name": name},
		as_dict=False,
	)

	timeline_items = dict(data)

	for date, count in timeline_items.items():
		timestamp = get_timestamp(date)
		out.update({timestamp: count})

	return out


def get_dashboard_info(party_type, party, loyalty_program=None):
	current_fiscal_year = get_fiscal_year(nowdate(), as_dict=True)

	doctype = "Sales Invoice" if party_type == "Customer" else "Purchase Invoice"

	companies = vmraid.get_all(
		doctype, filters={"docstatus": 1, party_type.lower(): party}, distinct=1, fields=["company"]
	)

	company_wise_info = []

	company_wise_grand_total = vmraid.get_all(
		doctype,
		filters={
			"docstatus": 1,
			party_type.lower(): party,
			"posting_date": (
				"between",
				[current_fiscal_year.year_start_date, current_fiscal_year.year_end_date],
			),
		},
		group_by="company",
		fields=[
			"company",
			"sum(grand_total) as grand_total",
			"sum(base_grand_total) as base_grand_total",
		],
	)

	loyalty_point_details = []

	if party_type == "Customer":
		loyalty_point_details = vmraid._dict(
			vmraid.get_all(
				"Loyalty Point Entry",
				filters={
					"customer": party,
					"expiry_date": (">=", getdate()),
				},
				group_by="company",
				fields=["company", "sum(loyalty_points) as loyalty_points"],
				as_list=1,
			)
		)

	company_wise_billing_this_year = vmraid._dict()

	for d in company_wise_grand_total:
		company_wise_billing_this_year.setdefault(
			d.company, {"grand_total": d.grand_total, "base_grand_total": d.base_grand_total}
		)

	company_wise_total_unpaid = vmraid._dict(
		vmraid.db.sql(
			"""
		select company, sum(debit_in_account_currency) - sum(credit_in_account_currency)
		from `tabGL Entry`
		where party_type = %s and party=%s
		and is_cancelled = 0
		group by company""",
			(party_type, party),
		)
	)

	for d in companies:
		company_default_currency = vmraid.db.get_value("Company", d.company, "default_currency")
		party_account_currency = get_party_account_currency(party_type, party, d.company)

		if party_account_currency == company_default_currency:
			billing_this_year = flt(
				company_wise_billing_this_year.get(d.company, {}).get("base_grand_total")
			)
		else:
			billing_this_year = flt(company_wise_billing_this_year.get(d.company, {}).get("grand_total"))

		total_unpaid = flt(company_wise_total_unpaid.get(d.company))

		if loyalty_point_details:
			loyalty_points = loyalty_point_details.get(d.company)

		info = {}
		info["billing_this_year"] = flt(billing_this_year) if billing_this_year else 0
		info["currency"] = party_account_currency
		info["total_unpaid"] = flt(total_unpaid) if total_unpaid else 0
		info["company"] = d.company

		if party_type == "Customer" and loyalty_point_details:
			info["loyalty_points"] = loyalty_points

		if party_type == "Supplier":
			info["total_unpaid"] = -1 * info["total_unpaid"]

		company_wise_info.append(info)

	return company_wise_info


def get_party_shipping_address(doctype, name):
	"""
	Returns an Address name (best guess) for the given doctype and name for which `address_type == 'Shipping'` is true.
	and/or `is_shipping_address = 1`.

	It returns an empty string if there is no matching record.

	:param doctype: Party Doctype
	:param name: Party name
	:return: String
	"""
	out = vmraid.db.sql(
		"SELECT dl.parent "
		"from `tabDynamic Link` dl join `tabAddress` ta on dl.parent=ta.name "
		"where "
		"dl.link_doctype=%s "
		"and dl.link_name=%s "
		'and dl.parenttype="Address" '
		"and ifnull(ta.disabled, 0) = 0 and"
		'(ta.address_type="Shipping" or ta.is_shipping_address=1) '
		"order by ta.is_shipping_address desc, ta.address_type desc limit 1",
		(doctype, name),
	)
	if out:
		return out[0][0]
	else:
		return ""


def get_partywise_advanced_payment_amount(
	party_type, posting_date=None, future_payment=0, company=None
):
	cond = "1=1"
	if posting_date:
		if future_payment:
			cond = "posting_date <= '{0}' OR DATE(creation) <= '{0}' " "".format(posting_date)
		else:
			cond = "posting_date <= '{0}'".format(posting_date)

	if company:
		cond += "and company = {0}".format(vmraid.db.escape(company))

	data = vmraid.db.sql(
		""" SELECT party, sum({0}) as amount
		FROM `tabGL Entry`
		WHERE
			party_type = %s and against_voucher is null
			and is_cancelled = 0
			and {1} GROUP BY party""".format(
			("credit") if party_type == "Customer" else "debit", cond
		),
		party_type,
	)

	if data:
		return vmraid._dict(data)


def get_default_contact(doctype, name):
	"""
	Returns default contact for the given doctype and name.
	Can be ordered by `contact_type` to either is_primary_contact or is_billing_contact.
	"""
	out = vmraid.db.sql(
		"""
			SELECT dl.parent, c.is_primary_contact, c.is_billing_contact
			FROM `tabDynamic Link` dl
			INNER JOIN tabContact c ON c.name = dl.parent
			WHERE
				dl.link_doctype=%s AND
				dl.link_name=%s AND
				dl.parenttype = "Contact"
			ORDER BY is_primary_contact DESC, is_billing_contact DESC
		""",
		(doctype, name),
	)
	if out:
		try:
			return out[0][0]
		except Exception:
			return None
	else:
		return None
