# Copyright (c) 2015, VMRaid and contributors
# For license information, please see license.txt


import vmraid
from vmraid.model.document import Document


class WorkOrderItem(Document):
	pass


def on_doctype_update():
	vmraid.db.add_index("Work Order Item", ["item_code", "source_warehouse"])
