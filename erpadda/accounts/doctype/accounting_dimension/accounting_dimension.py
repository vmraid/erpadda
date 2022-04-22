# Copyright (c) 2019, VMRaid and contributors
# For license information, please see license.txt


import json

import vmraid
from vmraid import _, scrub
from vmraid.custom.doctype.custom_field.custom_field import create_custom_field
from vmraid.model import core_doctypes_list
from vmraid.model.document import Document
from vmraid.utils import cstr


class AccountingDimension(Document):
	def before_insert(self):
		self.set_fieldname_and_label()

	def validate(self):
		if self.document_type in core_doctypes_list + (
			"Accounting Dimension",
			"Project",
			"Cost Center",
			"Accounting Dimension Detail",
			"Company",
			"Account",
		):

			msg = _("Not allowed to create accounting dimension for {0}").format(self.document_type)
			vmraid.throw(msg)

		exists = vmraid.db.get_value(
			"Accounting Dimension", {"document_type": self.document_type}, ["name"]
		)

		if exists and self.is_new():
			vmraid.throw(_("Document Type already used as a dimension"))

		if not self.is_new():
			self.validate_document_type_change()

	def validate_document_type_change(self):
		doctype_before_save = vmraid.db.get_value("Accounting Dimension", self.name, "document_type")
		if doctype_before_save != self.document_type:
			message = _("Cannot change Reference Document Type.")
			message += _("Please create a new Accounting Dimension if required.")
			vmraid.throw(message)

	def after_insert(self):
		if vmraid.flags.in_test:
			make_dimension_in_accounting_doctypes(doc=self)
		else:
			vmraid.enqueue(make_dimension_in_accounting_doctypes, doc=self, queue="long")

	def on_trash(self):
		if vmraid.flags.in_test:
			delete_accounting_dimension(doc=self)
		else:
			vmraid.enqueue(delete_accounting_dimension, doc=self, queue="long")

	def set_fieldname_and_label(self):
		if not self.label:
			self.label = cstr(self.document_type)

		if not self.fieldname:
			self.fieldname = scrub(self.label)

	def on_update(self):
		vmraid.flags.accounting_dimensions = None


def make_dimension_in_accounting_doctypes(doc, doclist=None):
	if not doclist:
		doclist = get_doctypes_with_dimensions()

	doc_count = len(get_accounting_dimensions())
	count = 0

	for doctype in doclist:

		if (doc_count + 1) % 2 == 0:
			insert_after_field = "dimension_col_break"
		else:
			insert_after_field = "accounting_dimensions_section"

		df = {
			"fieldname": doc.fieldname,
			"label": doc.label,
			"fieldtype": "Link",
			"options": doc.document_type,
			"insert_after": insert_after_field,
			"owner": "Administrator",
		}

		meta = vmraid.get_meta(doctype, cached=False)
		fieldnames = [d.fieldname for d in meta.get("fields")]

		if df["fieldname"] not in fieldnames:
			if doctype == "Budget":
				add_dimension_to_budget_doctype(df.copy(), doc)
			else:
				create_custom_field(doctype, df)

		count += 1

		vmraid.publish_progress(count * 100 / len(doclist), title=_("Creating Dimensions..."))
		vmraid.clear_cache(doctype=doctype)


def add_dimension_to_budget_doctype(df, doc):
	df.update(
		{
			"insert_after": "cost_center",
			"depends_on": "eval:doc.budget_against == '{0}'".format(doc.document_type),
		}
	)

	create_custom_field("Budget", df)

	property_setter = vmraid.db.exists("Property Setter", "Budget-budget_against-options")

	if property_setter:
		property_setter_doc = vmraid.get_doc("Property Setter", "Budget-budget_against-options")
		property_setter_doc.value = property_setter_doc.value + "\n" + doc.document_type
		property_setter_doc.save()

		vmraid.clear_cache(doctype="Budget")
	else:
		vmraid.get_doc(
			{
				"doctype": "Property Setter",
				"doctype_or_field": "DocField",
				"doc_type": "Budget",
				"field_name": "budget_against",
				"property": "options",
				"property_type": "Text",
				"value": "\nCost Center\nProject\n" + doc.document_type,
			}
		).insert(ignore_permissions=True)


def delete_accounting_dimension(doc):
	doclist = get_doctypes_with_dimensions()

	vmraid.db.sql(
		"""
		DELETE FROM `tabCustom Field`
		WHERE fieldname = %s
		AND dt IN (%s)"""
		% ("%s", ", ".join(["%s"] * len(doclist))),  # nosec
		tuple([doc.fieldname] + doclist),
	)

	vmraid.db.sql(
		"""
		DELETE FROM `tabProperty Setter`
		WHERE field_name = %s
		AND doc_type IN (%s)"""
		% ("%s", ", ".join(["%s"] * len(doclist))),  # nosec
		tuple([doc.fieldname] + doclist),
	)

	budget_against_property = vmraid.get_doc("Property Setter", "Budget-budget_against-options")
	value_list = budget_against_property.value.split("\n")[3:]

	if doc.document_type in value_list:
		value_list.remove(doc.document_type)

	budget_against_property.value = "\nCost Center\nProject\n" + "\n".join(value_list)
	budget_against_property.save()

	for doctype in doclist:
		vmraid.clear_cache(doctype=doctype)


@vmraid.whitelist()
def disable_dimension(doc):
	if vmraid.flags.in_test:
		toggle_disabling(doc=doc)
	else:
		vmraid.enqueue(toggle_disabling, doc=doc)


def toggle_disabling(doc):
	doc = json.loads(doc)

	if doc.get("disabled"):
		df = {"read_only": 1}
	else:
		df = {"read_only": 0}

	doclist = get_doctypes_with_dimensions()

	for doctype in doclist:
		field = vmraid.db.get_value("Custom Field", {"dt": doctype, "fieldname": doc.get("fieldname")})
		if field:
			custom_field = vmraid.get_doc("Custom Field", field)
			custom_field.update(df)
			custom_field.save()

		vmraid.clear_cache(doctype=doctype)


def get_doctypes_with_dimensions():
	return vmraid.get_hooks("accounting_dimension_doctypes")


def get_accounting_dimensions(as_list=True, filters=None):

	if not filters:
		filters = {"disabled": 0}

	if vmraid.flags.accounting_dimensions is None:
		vmraid.flags.accounting_dimensions = vmraid.get_all(
			"Accounting Dimension",
			fields=["label", "fieldname", "disabled", "document_type"],
			filters=filters,
		)

	if as_list:
		return [d.fieldname for d in vmraid.flags.accounting_dimensions]
	else:
		return vmraid.flags.accounting_dimensions


def get_checks_for_pl_and_bs_accounts():
	dimensions = vmraid.db.sql(
		"""SELECT p.label, p.disabled, p.fieldname, c.default_dimension, c.company, c.mandatory_for_pl, c.mandatory_for_bs
		FROM `tabAccounting Dimension`p ,`tabAccounting Dimension Detail` c
		WHERE p.name = c.parent""",
		as_dict=1,
	)

	return dimensions


def get_dimension_with_children(doctype, dimension):

	if isinstance(dimension, list):
		dimension = dimension[0]

	all_dimensions = []
	lft, rgt = vmraid.db.get_value(doctype, dimension, ["lft", "rgt"])
	children = vmraid.get_all(
		doctype, filters={"lft": [">=", lft], "rgt": ["<=", rgt]}, order_by="lft"
	)
	all_dimensions += [c.name for c in children]

	return all_dimensions


@vmraid.whitelist()
def get_dimensions(with_cost_center_and_project=False):
	dimension_filters = vmraid.db.sql(
		"""
		SELECT label, fieldname, document_type
		FROM `tabAccounting Dimension`
		WHERE disabled = 0
	""",
		as_dict=1,
	)

	default_dimensions = vmraid.db.sql(
		"""SELECT p.fieldname, c.company, c.default_dimension
		FROM `tabAccounting Dimension Detail` c, `tabAccounting Dimension` p
		WHERE c.parent = p.name""",
		as_dict=1,
	)

	if with_cost_center_and_project:
		dimension_filters.extend(
			[
				{"fieldname": "cost_center", "document_type": "Cost Center"},
				{"fieldname": "project", "document_type": "Project"},
			]
		)

	default_dimensions_map = {}
	for dimension in default_dimensions:
		default_dimensions_map.setdefault(dimension.company, {})
		default_dimensions_map[dimension.company][dimension.fieldname] = dimension.default_dimension

	return dimension_filters, default_dimensions_map
