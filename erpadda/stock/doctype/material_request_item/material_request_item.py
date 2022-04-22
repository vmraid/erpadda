# Copyright (c) 2015, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt

# For license information, please see license.txt


import vmraid
from vmraid.model.document import Document


class MaterialRequestItem(Document):
	pass


def on_doctype_update():
	vmraid.db.add_index("Material Request Item", ["item_code", "warehouse"])
