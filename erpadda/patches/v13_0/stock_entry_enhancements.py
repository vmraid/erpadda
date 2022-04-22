# Copyright(c) 2020, VMRaid Technologies Pvt.Ltd.and Contributors
# License: GNU General Public License v3.See license.txt


import vmraid


def execute():
	vmraid.reload_doc("stock", "doctype", "stock_entry")
	if vmraid.db.has_column("Stock Entry", "add_to_transit"):
		vmraid.db.sql(
			"""
            UPDATE `tabStock Entry` SET
            stock_entry_type = 'Material Transfer',
            purpose = 'Material Transfer',
            add_to_transit = 1 WHERE stock_entry_type = 'Send to Warehouse'
            """
		)

		vmraid.db.sql(
			"""UPDATE `tabStock Entry` SET
            stock_entry_type = 'Material Transfer',
            purpose = 'Material Transfer'
            WHERE stock_entry_type = 'Receive at Warehouse'
            """
		)

		vmraid.reload_doc("stock", "doctype", "warehouse_type")
		if not vmraid.db.exists("Warehouse Type", "Transit"):
			doc = vmraid.new_doc("Warehouse Type")
			doc.name = "Transit"
			doc.insert()

		vmraid.reload_doc("stock", "doctype", "stock_entry_type")
		vmraid.delete_doc_if_exists("Stock Entry Type", "Send to Warehouse")
		vmraid.delete_doc_if_exists("Stock Entry Type", "Receive at Warehouse")
