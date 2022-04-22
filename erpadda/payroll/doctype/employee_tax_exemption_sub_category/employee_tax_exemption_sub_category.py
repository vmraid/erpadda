# Copyright (c) 2018, VMRaid and contributors
# For license information, please see license.txt


import vmraid
from vmraid import _
from vmraid.model.document import Document
from vmraid.utils import flt


class EmployeeTaxExemptionSubCategory(Document):
	def validate(self):
		category_max_amount = vmraid.db.get_value(
			"Employee Tax Exemption Category", self.exemption_category, "max_amount"
		)
		if flt(self.max_amount) > flt(category_max_amount):
			vmraid.throw(
				_(
					"Max Exemption Amount cannot be greater than maximum exemption amount {0} of Tax Exemption Category {1}"
				).format(category_max_amount, self.exemption_category)
			)
