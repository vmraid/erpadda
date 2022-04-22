# Copyright (c) 2015, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


from collections import defaultdict

import vmraid
from vmraid import _, throw
from vmraid.contacts.address_and_contact import load_address_and_contact
from vmraid.utils import cint, flt
from vmraid.utils.nestedset import NestedSet

from erpadda.stock import get_warehouse_account


class Warehouse(NestedSet):
	nsm_parent_field = "parent_warehouse"

	def autoname(self):
		if self.company:
			suffix = " - " + vmraid.get_cached_value("Company", self.company, "abbr")
			if not self.warehouse_name.endswith(suffix):
				self.name = self.warehouse_name + suffix
				return

		self.name = self.warehouse_name

	def onload(self):
		"""load account name for General Ledger Report"""
		if self.company and cint(
			vmraid.db.get_value("Company", self.company, "enable_perpetual_inventory")
		):
			account = self.account or get_warehouse_account(self)

			if account:
				self.set_onload("account", account)
		load_address_and_contact(self)

	def on_update(self):
		self.update_nsm_model()

	def update_nsm_model(self):
		vmraid.utils.nestedset.update_nsm(self)

	def on_trash(self):
		# delete bin
		bins = vmraid.get_all("Bin", fields="*", filters={"warehouse": self.name})
		for d in bins:
			if (
				d["actual_qty"]
				or d["reserved_qty"]
				or d["ordered_qty"]
				or d["indented_qty"]
				or d["projected_qty"]
				or d["planned_qty"]
			):
				throw(
					_("Warehouse {0} can not be deleted as quantity exists for Item {1}").format(
						self.name, d["item_code"]
					)
				)

		if self.check_if_sle_exists():
			throw(_("Warehouse can not be deleted as stock ledger entry exists for this warehouse."))

		if self.check_if_child_exists():
			throw(_("Child warehouse exists for this warehouse. You can not delete this warehouse."))

		vmraid.db.delete("Bin", filters={"warehouse": self.name})
		self.update_nsm_model()
		self.unlink_from_items()

	def check_if_sle_exists(self):
		return vmraid.db.exists("Stock Ledger Entry", {"warehouse": self.name})

	def check_if_child_exists(self):
		return vmraid.db.exists("Warehouse", {"parent_warehouse": self.name})

	def convert_to_group_or_ledger(self):
		if self.is_group:
			self.convert_to_ledger()
		else:
			self.convert_to_group()

	def convert_to_ledger(self):
		if self.check_if_child_exists():
			vmraid.throw(_("Warehouses with child nodes cannot be converted to ledger"))
		elif self.check_if_sle_exists():
			throw(_("Warehouses with existing transaction can not be converted to ledger."))
		else:
			self.is_group = 0
			self.save()
			return 1

	def convert_to_group(self):
		if self.check_if_sle_exists():
			throw(_("Warehouses with existing transaction can not be converted to group."))
		else:
			self.is_group = 1
			self.save()
			return 1

	def unlink_from_items(self):
		vmraid.db.set_value("Item Default", {"default_warehouse": self.name}, "default_warehouse", None)


@vmraid.whitelist()
def get_children(doctype, parent=None, company=None, is_root=False):
	if is_root:
		parent = ""

	fields = ["name as value", "is_group as expandable"]
	filters = [
		["docstatus", "<", "2"],
		['ifnull(`parent_warehouse`, "")', "=", parent],
		["company", "in", (company, None, "")],
	]

	warehouses = vmraid.get_list(doctype, fields=fields, filters=filters, order_by="name")

	company_currency = ""
	if company:
		company_currency = vmraid.get_cached_value("Company", company, "default_currency")

	warehouse_wise_value = get_warehouse_wise_stock_value(company)

	# return warehouses
	for wh in warehouses:
		wh["balance"] = warehouse_wise_value.get(wh.value)
		if company_currency:
			wh["company_currency"] = company_currency
	return warehouses


def get_warehouse_wise_stock_value(company):
	warehouses = vmraid.get_all(
		"Warehouse", fields=["name", "parent_warehouse"], filters={"company": company}
	)
	parent_warehouse = {d.name: d.parent_warehouse for d in warehouses}

	filters = {"warehouse": ("in", [data.name for data in warehouses])}
	bin_data = vmraid.get_all(
		"Bin",
		fields=["sum(stock_value) as stock_value", "warehouse"],
		filters=filters,
		group_by="warehouse",
	)

	warehouse_wise_stock_value = defaultdict(float)
	for row in bin_data:
		if not row.stock_value:
			continue

		warehouse_wise_stock_value[row.warehouse] = row.stock_value
		update_value_in_parent_warehouse(
			warehouse_wise_stock_value, parent_warehouse, row.warehouse, row.stock_value
		)

	return warehouse_wise_stock_value


def update_value_in_parent_warehouse(
	warehouse_wise_stock_value, parent_warehouse_dict, warehouse, stock_value
):
	parent_warehouse = parent_warehouse_dict.get(warehouse)
	if not parent_warehouse:
		return

	warehouse_wise_stock_value[parent_warehouse] += flt(stock_value)
	update_value_in_parent_warehouse(
		warehouse_wise_stock_value, parent_warehouse_dict, parent_warehouse, stock_value
	)


@vmraid.whitelist()
def add_node():
	from vmraid.desk.treeview import make_tree_args

	args = make_tree_args(**vmraid.form_dict)

	if cint(args.is_root):
		args.parent_warehouse = None

	vmraid.get_doc(args).insert()


@vmraid.whitelist()
def convert_to_group_or_ledger(docname=None):
	if not docname:
		docname = vmraid.form_dict.docname
	return vmraid.get_doc("Warehouse", docname).convert_to_group_or_ledger()


def get_child_warehouses(warehouse):
	from vmraid.utils.nestedset import get_descendants_of

	children = get_descendants_of("Warehouse", warehouse, ignore_permissions=True, order_by="lft")
	return children + [warehouse]  # append self for backward compatibility


def get_warehouses_based_on_account(account, company=None):
	warehouses = []
	for d in vmraid.get_all("Warehouse", fields=["name", "is_group"], filters={"account": account}):
		if d.is_group:
			warehouses.extend(get_child_warehouses(d.name))
		else:
			warehouses.append(d.name)

	if (
		not warehouses
		and company
		and vmraid.get_cached_value("Company", company, "default_inventory_account") == account
	):
		warehouses = [d.name for d in vmraid.get_all("Warehouse", filters={"is_group": 0})]

	if not warehouses:
		vmraid.throw(_("Warehouse not found against the account {0}").format(account))

	return warehouses
