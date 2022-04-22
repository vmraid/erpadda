# Copyright (c) 2015, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid
from vmraid.model.document import Document


class SalesOrderItem(Document):
	pass


def on_doctype_update():
	vmraid.db.add_index("Sales Order Item", ["item_code", "warehouse"])
