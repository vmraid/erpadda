# Copyright (c) 2015, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt

import vmraid

test_records = vmraid.get_test_records("Product Bundle")


def make_product_bundle(parent, items, qty=None):
	if vmraid.db.exists("Product Bundle", parent):
		return vmraid.get_doc("Product Bundle", parent)

	product_bundle = vmraid.get_doc({"doctype": "Product Bundle", "new_item_code": parent})

	for item in items:
		product_bundle.append("items", {"item_code": item, "qty": qty or 1})

	product_bundle.insert()

	return product_bundle
