# Copyright (c) 2018, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid


def execute():
	vmraid.reload_doc("stock", "doctype", "item")
	vmraid.db.sql(
		""" update `tabItem` set include_item_in_manufacturing = 1
		where ifnull(is_stock_item, 0) = 1"""
	)

	for doctype in ["BOM Item", "Work Order Item", "BOM Explosion Item"]:
		vmraid.reload_doc("manufacturing", "doctype", vmraid.scrub(doctype))

		vmraid.db.sql(
			""" update `tab{0}` child, tabItem item
			set
				child.include_item_in_manufacturing = 1
			where
				child.item_code = item.name and ifnull(item.is_stock_item, 0) = 1
		""".format(
				doctype
			)
		)
