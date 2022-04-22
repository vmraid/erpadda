# Copyright (c) 2020, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid


def execute():
	warehouse_perm = vmraid.get_all(
		"User Permission",
		fields=["count(*) as p_count", "is_default", "user"],
		filters={"allow": "Warehouse"},
		group_by="user",
	)

	if not warehouse_perm:
		return

	execute_patch = False
	for perm_data in warehouse_perm:
		if perm_data.p_count == 1 or (
			perm_data.p_count > 1
			and vmraid.get_all(
				"User Permission",
				filters={"user": perm_data.user, "allow": "warehouse", "is_default": 1},
				limit=1,
			)
		):
			execute_patch = True
			break

	if not execute_patch:
		return

	for doctype in ["Sales Invoice", "Delivery Note"]:
		if not vmraid.get_meta(doctype + " Item").get_field("target_warehouse").hidden:
			continue

		cond = ""
		if doctype == "Sales Invoice":
			cond = " AND parent_doc.update_stock = 1"

		data = vmraid.db.sql(
			""" SELECT parent_doc.name as name, child_doc.name as child_name
			FROM
				`tab{doctype}` parent_doc, `tab{doctype} Item` child_doc
			WHERE
				parent_doc.name = child_doc.parent AND parent_doc.docstatus < 2
				AND child_doc.target_warehouse is not null AND child_doc.target_warehouse != ''
				AND child_doc.creation > '2020-04-16' {cond}
		""".format(
				doctype=doctype, cond=cond
			),
			as_dict=1,
		)

		if data:
			names = [d.child_name for d in data]
			vmraid.db.sql(
				""" UPDATE `tab{0} Item` set target_warehouse = null
				WHERE name in ({1}) """.format(
					doctype, ",".join(["%s"] * len(names))
				),
				tuple(names),
			)

			vmraid.db.sql(
				""" UPDATE `tabPacked Item` set target_warehouse = null
				WHERE parenttype = '{0}' and parent_detail_docname in ({1})
			""".format(
					doctype, ",".join(["%s"] * len(names))
				),
				tuple(names),
			)

			parent_names = list(set([d.name for d in data]))

			for d in parent_names:
				doc = vmraid.get_doc(doctype, d)
				if doc.docstatus != 1:
					continue

				doc.docstatus = 2
				doc.update_stock_ledger()
				doc.make_gl_entries_on_cancel(repost_future_gle=False)

				# update stock & gl entries for submit state of PR
				doc.docstatus = 1
				doc.update_stock_ledger()
				doc.make_gl_entries()

	if vmraid.get_meta("Sales Order Item").get_field("target_warehouse").hidden:
		vmraid.db.sql(
			""" UPDATE `tabSales Order Item` set target_warehouse = null
			WHERE creation > '2020-04-16' and docstatus < 2 """
		)

		vmraid.db.sql(
			""" UPDATE `tabPacked Item` set target_warehouse = null
			WHERE creation > '2020-04-16' and docstatus < 2 and parenttype = 'Sales Order' """
		)
