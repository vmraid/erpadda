# Copyright (c) 2015, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt

# For license information, please see license.txt


import vmraid
from vmraid.model.document import Document


class BuyingSettings(Document):
	def validate(self):
		for key in ["supplier_group", "supp_master_name", "maintain_same_rate", "buying_price_list"]:
			vmraid.db.set_default(key, self.get(key, ""))

		from erpadda.setup.doctype.naming_series.naming_series import set_by_naming_series

		set_by_naming_series(
			"Supplier",
			"supplier_name",
			self.get("supp_master_name") == "Naming Series",
			hide_name_field=False,
		)
