# Copyright (c) 2018, VMRaid and contributors
# For license information, please see license.txt


import vmraid
from vmraid import _
from vmraid.model.document import Document


class ItemTaxTemplate(Document):
	def validate(self):
		self.validate_tax_accounts()

	def autoname(self):
		if self.company and self.title:
			abbr = vmraid.get_cached_value("Company", self.company, "abbr")
			self.name = "{0} - {1}".format(self.title, abbr)

	def validate_tax_accounts(self):
		"""Check whether Tax Rate is not entered twice for same Tax Type"""
		check_list = []
		for d in self.get("taxes"):
			if d.tax_type:
				account_type = vmraid.db.get_value("Account", d.tax_type, "account_type")

				if account_type not in [
					"Tax",
					"Chargeable",
					"Income Account",
					"Expense Account",
					"Expenses Included In Valuation",
				]:
					vmraid.throw(
						_(
							"Item Tax Row {0} must have account of type Tax or Income or Expense or Chargeable"
						).format(d.idx)
					)
				else:
					if d.tax_type in check_list:
						vmraid.throw(_("{0} entered twice in Item Tax").format(d.tax_type))
					else:
						check_list.append(d.tax_type)
