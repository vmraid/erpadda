# Copyright (c) 2021, VMRaid and contributors
# For license information, please see license.txt


import vmraid
from vmraid import _
from vmraid.desk.notifications import clear_notifications
from vmraid.model.document import Document
from vmraid.utils import cint


class TransactionDeletionRecord(Document):
	def validate(self):
		vmraid.only_for("System Manager")
		self.validate_doctypes_to_be_ignored()

	def validate_doctypes_to_be_ignored(self):
		doctypes_to_be_ignored_list = get_doctypes_to_be_ignored()
		for doctype in self.doctypes_to_be_ignored:
			if doctype.doctype_name not in doctypes_to_be_ignored_list:
				vmraid.throw(
					_(
						"DocTypes should not be added manually to the 'Excluded DocTypes' table. You are only allowed to remove entries from it."
					),
					title=_("Not Allowed"),
				)

	def before_submit(self):
		if not self.doctypes_to_be_ignored:
			self.populate_doctypes_to_be_ignored_table()

		self.delete_bins()
		self.delete_lead_addresses()
		self.reset_company_values()
		clear_notifications()
		self.delete_company_transactions()

	def populate_doctypes_to_be_ignored_table(self):
		doctypes_to_be_ignored_list = get_doctypes_to_be_ignored()
		for doctype in doctypes_to_be_ignored_list:
			self.append("doctypes_to_be_ignored", {"doctype_name": doctype})

	def delete_bins(self):
		vmraid.db.sql(
			"""delete from tabBin where warehouse in
				(select name from tabWarehouse where company=%s)""",
			self.company,
		)

	def delete_lead_addresses(self):
		"""Delete addresses to which leads are linked"""
		leads = vmraid.get_all("Lead", filters={"company": self.company})
		leads = ["'%s'" % row.get("name") for row in leads]
		addresses = []
		if leads:
			addresses = vmraid.db.sql_list(
				"""select parent from `tabDynamic Link` where link_name
				in ({leads})""".format(
					leads=",".join(leads)
				)
			)

			if addresses:
				addresses = ["%s" % vmraid.db.escape(addr) for addr in addresses]

				vmraid.db.sql(
					"""delete from tabAddress where name in ({addresses}) and
					name not in (select distinct dl1.parent from `tabDynamic Link` dl1
					inner join `tabDynamic Link` dl2 on dl1.parent=dl2.parent
					and dl1.link_doctype<>dl2.link_doctype)""".format(
						addresses=",".join(addresses)
					)
				)

				vmraid.db.sql(
					"""delete from `tabDynamic Link` where link_doctype='Lead'
					and parenttype='Address' and link_name in ({leads})""".format(
						leads=",".join(leads)
					)
				)

			vmraid.db.sql(
				"""update tabCustomer set lead_name=NULL where lead_name in ({leads})""".format(
					leads=",".join(leads)
				)
			)

	def reset_company_values(self):
		company_obj = vmraid.get_doc("Company", self.company)
		company_obj.total_monthly_sales = 0
		company_obj.sales_monthly_history = None
		company_obj.save()

	def delete_company_transactions(self):
		doctypes_to_be_ignored_list = self.get_doctypes_to_be_ignored_list()
		docfields = self.get_doctypes_with_company_field(doctypes_to_be_ignored_list)

		tables = self.get_all_child_doctypes()
		for docfield in docfields:
			if docfield["parent"] != self.doctype:
				no_of_docs = self.get_number_of_docs_linked_with_specified_company(
					docfield["parent"], docfield["fieldname"]
				)

				if no_of_docs > 0:
					self.delete_version_log(docfield["parent"], docfield["fieldname"])
					self.delete_communications(docfield["parent"], docfield["fieldname"])
					self.populate_doctypes_table(tables, docfield["parent"], no_of_docs)

					self.delete_child_tables(docfield["parent"], docfield["fieldname"])
					self.delete_docs_linked_with_specified_company(docfield["parent"], docfield["fieldname"])

					naming_series = vmraid.db.get_value("DocType", docfield["parent"], "autoname")
					if naming_series:
						if "#" in naming_series:
							self.update_naming_series(naming_series, docfield["parent"])

	def get_doctypes_to_be_ignored_list(self):
		singles = vmraid.get_all("DocType", filters={"issingle": 1}, pluck="name")
		doctypes_to_be_ignored_list = singles
		for doctype in self.doctypes_to_be_ignored:
			doctypes_to_be_ignored_list.append(doctype.doctype_name)

		return doctypes_to_be_ignored_list

	def get_doctypes_with_company_field(self, doctypes_to_be_ignored_list):
		docfields = vmraid.get_all(
			"DocField",
			filters={
				"fieldtype": "Link",
				"options": "Company",
				"parent": ["not in", doctypes_to_be_ignored_list],
			},
			fields=["parent", "fieldname"],
		)

		return docfields

	def get_all_child_doctypes(self):
		return vmraid.get_all("DocType", filters={"istable": 1}, pluck="name")

	def get_number_of_docs_linked_with_specified_company(self, doctype, company_fieldname):
		return vmraid.db.count(doctype, {company_fieldname: self.company})

	def populate_doctypes_table(self, tables, doctype, no_of_docs):
		if doctype not in tables:
			self.append("doctypes", {"doctype_name": doctype, "no_of_docs": no_of_docs})

	def delete_child_tables(self, doctype, company_fieldname):
		parent_docs_to_be_deleted = vmraid.get_all(
			doctype, {company_fieldname: self.company}, pluck="name"
		)

		child_tables = vmraid.get_all(
			"DocField", filters={"fieldtype": "Table", "parent": doctype}, pluck="options"
		)

		for table in child_tables:
			vmraid.db.delete(table, {"parent": ["in", parent_docs_to_be_deleted]})

	def delete_docs_linked_with_specified_company(self, doctype, company_fieldname):
		vmraid.db.delete(doctype, {company_fieldname: self.company})

	def update_naming_series(self, naming_series, doctype_name):
		if "." in naming_series:
			prefix, hashes = naming_series.rsplit(".", 1)
		else:
			prefix, hashes = naming_series.rsplit("{", 1)
		last = vmraid.db.sql(
			"""select max(name) from `tab{0}`
						where name like %s""".format(
				doctype_name
			),
			prefix + "%",
		)
		if last and last[0][0]:
			last = cint(last[0][0].replace(prefix, ""))
		else:
			last = 0

		vmraid.db.sql("""update tabSeries set current = %s where name=%s""", (last, prefix))

	def delete_version_log(self, doctype, company_fieldname):
		vmraid.db.sql(
			"""delete from `tabVersion` where ref_doctype=%s and docname in
			(select name from `tab{0}` where `{1}`=%s)""".format(
				doctype, company_fieldname
			),
			(doctype, self.company),
		)

	def delete_communications(self, doctype, company_fieldname):
		reference_docs = vmraid.get_all(doctype, filters={company_fieldname: self.company})
		reference_doc_names = [r.name for r in reference_docs]

		communications = vmraid.get_all(
			"Communication",
			filters={"reference_doctype": doctype, "reference_name": ["in", reference_doc_names]},
		)
		communication_names = [c.name for c in communications]

		vmraid.delete_doc("Communication", communication_names, ignore_permissions=True)


@vmraid.whitelist()
def get_doctypes_to_be_ignored():
	doctypes_to_be_ignored_list = [
		"Account",
		"Cost Center",
		"Warehouse",
		"Budget",
		"Party Account",
		"Employee",
		"Sales Taxes and Charges Template",
		"Purchase Taxes and Charges Template",
		"POS Profile",
		"BOM",
		"Company",
		"Bank Account",
		"Item Tax Template",
		"Mode of Payment",
		"Item Default",
		"Customer",
		"Supplier",
		"GST Account",
	]
	return doctypes_to_be_ignored_list
