# Copyright (c) 2015, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid
from vmraid.model.document import Document


class PurchaseOrderItem(Document):
	pass


def on_doctype_update():
	vmraid.db.add_index("Purchase Order Item", ["item_code", "warehouse"])
