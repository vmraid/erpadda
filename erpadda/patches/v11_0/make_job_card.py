# Copyright (c) 2017, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid

from erpadda.manufacturing.doctype.work_order.work_order import create_job_card


def execute():
	vmraid.reload_doc("manufacturing", "doctype", "work_order")
	vmraid.reload_doc("manufacturing", "doctype", "work_order_item")
	vmraid.reload_doc("manufacturing", "doctype", "job_card")
	vmraid.reload_doc("manufacturing", "doctype", "job_card_item")

	fieldname = vmraid.db.get_value(
		"DocField", {"fieldname": "work_order", "parent": "Timesheet"}, "fieldname"
	)
	if not fieldname:
		fieldname = vmraid.db.get_value(
			"DocField", {"fieldname": "production_order", "parent": "Timesheet"}, "fieldname"
		)
		if not fieldname:
			return

	for d in vmraid.get_all(
		"Timesheet", filters={fieldname: ["!=", ""], "docstatus": 0}, fields=[fieldname, "name"]
	):
		if d[fieldname]:
			doc = vmraid.get_doc("Work Order", d[fieldname])
			for row in doc.operations:
				create_job_card(doc, row, auto_create=True)
			vmraid.delete_doc("Timesheet", d.name)
