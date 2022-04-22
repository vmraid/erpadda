# Copyright (c) 2015, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid
from vmraid import _
from vmraid.utils import flt
from vmraid.utils.nestedset import NestedSet, get_root_of

from erpadda import get_default_currency


class SalesPerson(NestedSet):
	nsm_parent_field = "parent_sales_person"

	def validate(self):
		if not self.parent_sales_person:
			self.parent_sales_person = get_root_of("Sales Person")

		for d in self.get("targets") or []:
			if not flt(d.target_qty) and not flt(d.target_amount):
				vmraid.throw(_("Either target qty or target amount is mandatory."))
		self.validate_employee_id()

	def onload(self):
		self.load_dashboard_info()

	def load_dashboard_info(self):
		company_default_currency = get_default_currency()

		allocated_amount_against_order = flt(
			vmraid.db.get_value(
				"Sales Team",
				{"docstatus": 1, "parenttype": "Sales Order", "sales_person": self.sales_person_name},
				"sum(allocated_amount)",
			)
		)

		allocated_amount_against_invoice = flt(
			vmraid.db.get_value(
				"Sales Team",
				{"docstatus": 1, "parenttype": "Sales Invoice", "sales_person": self.sales_person_name},
				"sum(allocated_amount)",
			)
		)

		info = {}
		info["allocated_amount_against_order"] = allocated_amount_against_order
		info["allocated_amount_against_invoice"] = allocated_amount_against_invoice
		info["currency"] = company_default_currency

		self.set_onload("dashboard_info", info)

	def on_update(self):
		super(SalesPerson, self).on_update()
		self.validate_one_root()

	def get_email_id(self):
		if self.employee:
			user = vmraid.db.get_value("Employee", self.employee, "user_id")
			if not user:
				vmraid.throw(_("User ID not set for Employee {0}").format(self.employee))
			else:
				return vmraid.db.get_value("User", user, "email") or user

	def validate_employee_id(self):
		if self.employee:
			sales_person = vmraid.db.get_value("Sales Person", {"employee": self.employee})

			if sales_person and sales_person != self.name:
				vmraid.throw(
					_("Another Sales Person {0} exists with the same Employee id").format(sales_person)
				)


def on_doctype_update():
	vmraid.db.add_index("Sales Person", ["lft", "rgt"])


def get_timeline_data(doctype, name):

	out = {}

	out.update(
		dict(
			vmraid.db.sql(
				"""select
			unix_timestamp(dt.transaction_date), count(st.parenttype)
		from
			`tabSales Order` dt, `tabSales Team` st
		where
			st.sales_person = %s and st.parent = dt.name and dt.transaction_date > date_sub(curdate(), interval 1 year)
			group by dt.transaction_date """,
				name,
			)
		)
	)

	sales_invoice = dict(
		vmraid.db.sql(
			"""select
			unix_timestamp(dt.posting_date), count(st.parenttype)
		from
			`tabSales Invoice` dt, `tabSales Team` st
		where
			st.sales_person = %s and st.parent = dt.name and dt.posting_date > date_sub(curdate(), interval 1 year)
			group by dt.posting_date """,
			name,
		)
	)

	for key in sales_invoice:
		if out.get(key):
			out[key] += sales_invoice[key]
		else:
			out[key] = sales_invoice[key]

	delivery_note = dict(
		vmraid.db.sql(
			"""select
			unix_timestamp(dt.posting_date), count(st.parenttype)
		from
			`tabDelivery Note` dt, `tabSales Team` st
		where
			st.sales_person = %s and st.parent = dt.name and dt.posting_date > date_sub(curdate(), interval 1 year)
			group by dt.posting_date """,
			name,
		)
	)

	for key in delivery_note:
		if out.get(key):
			out[key] += delivery_note[key]
		else:
			out[key] = delivery_note[key]

	return out
