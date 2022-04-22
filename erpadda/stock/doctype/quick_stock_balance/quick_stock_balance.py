# Copyright (c) 2019, VMRaid and contributors
# For license information, please see license.txt


import vmraid
from vmraid import _
from vmraid.model.document import Document

from erpadda.stock.utils import get_stock_balance, get_stock_value_on


class QuickStockBalance(Document):
	pass


@vmraid.whitelist()
def get_stock_item_details(warehouse, date, item=None, barcode=None):
	out = {}
	if barcode:
		out["item"] = vmraid.db.get_value(
			"Item Barcode", filters={"barcode": barcode}, fieldname=["parent"]
		)
		if not out["item"]:
			vmraid.throw(_("Invalid Barcode. There is no Item attached to this barcode."))
	else:
		out["item"] = item

	barcodes = vmraid.db.get_values(
		"Item Barcode", filters={"parent": out["item"]}, fieldname=["barcode"]
	)

	out["barcodes"] = [x[0] for x in barcodes]
	out["qty"] = get_stock_balance(out["item"], warehouse, date)
	out["value"] = get_stock_value_on(warehouse, date, out["item"])
	out["image"] = vmraid.db.get_value("Item", filters={"name": out["item"]}, fieldname=["image"])
	return out
