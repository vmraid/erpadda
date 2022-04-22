# Copyright (c) 2015, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid
from vmraid import _
from vmraid.utils import formatdate

from erpadda.controllers.website_list_for_contact import get_customers_suppliers


def get_context(context):
	context.no_cache = 1
	context.show_sidebar = True
	context.doc = vmraid.get_doc(vmraid.form_dict.doctype, vmraid.form_dict.name)
	context.parents = vmraid.form_dict.parents
	context.doc.supplier = get_supplier()
	context.doc.rfq_links = get_link_quotation(context.doc.supplier, context.doc.name)
	unauthorized_user(context.doc.supplier)
	update_supplier_details(context)
	context["title"] = vmraid.form_dict.name


def get_supplier():
	doctype = vmraid.form_dict.doctype
	parties_doctype = (
		"Request for Quotation Supplier" if doctype == "Request for Quotation" else doctype
	)
	customers, suppliers = get_customers_suppliers(parties_doctype, vmraid.session.user)

	return suppliers[0] if suppliers else ""


def check_supplier_has_docname_access(supplier):
	status = True
	if vmraid.form_dict.name not in vmraid.db.sql_list(
		"""select parent from `tabRequest for Quotation Supplier`
		where supplier = %s""",
		(supplier,),
	):
		status = False
	return status


def unauthorized_user(supplier):
	status = check_supplier_has_docname_access(supplier) or False
	if status == False:
		vmraid.throw(_("Not Permitted"), vmraid.PermissionError)


def update_supplier_details(context):
	supplier_doc = vmraid.get_doc("Supplier", context.doc.supplier)
	context.doc.currency = supplier_doc.default_currency or vmraid.get_cached_value(
		"Company", context.doc.company, "default_currency"
	)
	context.doc.currency_symbol = vmraid.db.get_value(
		"Currency", context.doc.currency, "symbol", cache=True
	)
	context.doc.number_format = vmraid.db.get_value(
		"Currency", context.doc.currency, "number_format", cache=True
	)
	context.doc.buying_price_list = supplier_doc.default_price_list or ""


def get_link_quotation(supplier, rfq):
	quotation = vmraid.db.sql(
		""" select distinct `tabSupplier Quotation Item`.parent as name,
		`tabSupplier Quotation`.status, `tabSupplier Quotation`.transaction_date from
		`tabSupplier Quotation Item`, `tabSupplier Quotation` where `tabSupplier Quotation`.docstatus < 2 and
		`tabSupplier Quotation Item`.request_for_quotation =%(name)s and
		`tabSupplier Quotation Item`.parent = `tabSupplier Quotation`.name and
		`tabSupplier Quotation`.supplier = %(supplier)s order by `tabSupplier Quotation`.creation desc""",
		{"name": rfq, "supplier": supplier},
		as_dict=1,
	)

	for data in quotation:
		data.transaction_date = formatdate(data.transaction_date)

	return quotation or None
