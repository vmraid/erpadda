# Copyright (c) 2019, VMRaid and contributors
# For license information, please see license.txt


import vmraid
from vmraid import _
from vmraid.model.document import Document


class LoanType(Document):
	def validate(self):
		self.validate_accounts()

	def validate_accounts(self):
		for fieldname in [
			"payment_account",
			"loan_account",
			"interest_income_account",
			"penalty_income_account",
		]:
			company = vmraid.get_value("Account", self.get(fieldname), "company")

			if company and company != self.company:
				vmraid.throw(
					_("Account {0} does not belong to company {1}").format(
						vmraid.bold(self.get(fieldname)), vmraid.bold(self.company)
					)
				)

		if self.get("loan_account") == self.get("payment_account"):
			vmraid.throw(_("Loan Account and Payment Account cannot be same"))
