# Copyright (c) 2017, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid


def execute():
	vmraid.reload_doc("stock", "doctype", "item_barcode")
	if vmraid.get_all("Item Barcode", limit=1):
		return
	if "barcode" not in vmraid.db.get_table_columns("Item"):
		return

	items_barcode = vmraid.db.sql(
		"select name, barcode from tabItem where barcode is not null", as_dict=True
	)
	vmraid.reload_doc("stock", "doctype", "item")

	for item in items_barcode:
		barcode = item.barcode.strip()

		if barcode and "<" not in barcode:
			try:
				vmraid.get_doc(
					{
						"idx": 0,
						"doctype": "Item Barcode",
						"barcode": barcode,
						"parenttype": "Item",
						"parent": item.name,
						"parentfield": "barcodes",
					}
				).insert()
			except (vmraid.DuplicateEntryError, vmraid.UniqueValidationError):
				continue
