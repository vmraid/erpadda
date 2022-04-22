# Copyright (c) 2020, VMRaid and contributors
# For license information, please see license.txt


from vmraid.model.document import Document

# import vmraid
import erpadda


class IncomeTaxSlab(Document):
	def validate(self):
		if self.company:
			self.currency = erpadda.get_company_currency(self.company)
