# Copyright (c) 2021, VMRaid and contributors
# For license information, please see license.txt

import vmraid
from vmraid.model.document import Document
from vmraid.model.naming import set_name_by_naming_series


class Campaign(Document):
	def autoname(self):
		if vmraid.defaults.get_global_default("campaign_naming_by") != "Naming Series":
			self.name = self.campaign_name
		else:
			set_name_by_naming_series(self)
