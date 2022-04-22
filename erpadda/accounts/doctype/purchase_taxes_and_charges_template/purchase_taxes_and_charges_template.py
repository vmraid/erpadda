# Copyright (c) 2015, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid
from vmraid.model.document import Document

from erpadda.accounts.doctype.sales_taxes_and_charges_template.sales_taxes_and_charges_template import (
	valdiate_taxes_and_charges_template,
)


class PurchaseTaxesandChargesTemplate(Document):
	def validate(self):
		valdiate_taxes_and_charges_template(self)

	def autoname(self):
		if self.company and self.title:
			abbr = vmraid.get_cached_value("Company", self.company, "abbr")
			self.name = "{0} - {1}".format(self.title, abbr)
