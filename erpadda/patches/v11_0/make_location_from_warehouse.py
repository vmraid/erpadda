# Copyright (c) 2017, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid
from vmraid.utils.nestedset import rebuild_tree


def execute():
	if not vmraid.db.get_value("Asset", {"docstatus": ("<", 2)}, "name"):
		return
	vmraid.reload_doc("assets", "doctype", "location")
	vmraid.reload_doc("stock", "doctype", "warehouse")

	for d in vmraid.get_all(
		"Warehouse", fields=["warehouse_name", "is_group", "parent_warehouse"], order_by="lft asc"
	):
		try:
			loc = vmraid.new_doc("Location")
			loc.location_name = d.warehouse_name
			loc.is_group = d.is_group
			loc.flags.ignore_mandatory = True
			if d.parent_warehouse:
				loc.parent_location = get_parent_warehouse_name(d.parent_warehouse)

			loc.save(ignore_permissions=True)
		except vmraid.DuplicateEntryError:
			continue

	rebuild_tree("Location", "parent_location")


def get_parent_warehouse_name(warehouse):
	return vmraid.db.get_value("Warehouse", warehouse, "warehouse_name")
