# Copyright (c) 2018, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid
from vmraid.model.utils.rename_field import rename_field


def execute():
	vmraid.rename_doc("DocType", "Production Order", "Work Order", force=True)
	vmraid.reload_doc("manufacturing", "doctype", "work_order")

	vmraid.rename_doc("DocType", "Production Order Item", "Work Order Item", force=True)
	vmraid.reload_doc("manufacturing", "doctype", "work_order_item")

	vmraid.rename_doc("DocType", "Production Order Operation", "Work Order Operation", force=True)
	vmraid.reload_doc("manufacturing", "doctype", "work_order_operation")

	vmraid.reload_doc("projects", "doctype", "timesheet")
	vmraid.reload_doc("stock", "doctype", "stock_entry")
	rename_field("Timesheet", "production_order", "work_order")
	rename_field("Stock Entry", "production_order", "work_order")

	vmraid.rename_doc(
		"Report", "Production Orders in Progress", "Work Orders in Progress", force=True
	)
	vmraid.rename_doc("Report", "Completed Production Orders", "Completed Work Orders", force=True)
	vmraid.rename_doc("Report", "Open Production Orders", "Open Work Orders", force=True)
	vmraid.rename_doc(
		"Report", "Issued Items Against Production Order", "Issued Items Against Work Order", force=True
	)
	vmraid.rename_doc(
		"Report", "Production Order Stock Report", "Work Order Stock Report", force=True
	)
