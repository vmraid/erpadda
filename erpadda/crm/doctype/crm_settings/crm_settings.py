# Copyright (c) 2021, VMRaid and contributors
# For license information, please see license.txt

import vmraid
from vmraid.model.document import Document


class CRMSettings(Document):
	def validate(self):
		vmraid.db.set_default("campaign_naming_by", self.get("campaign_naming_by", ""))
