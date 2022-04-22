# Copyright (c) 2019, VMRaid and contributors
# For license information, please see license.txt


import vmraid
from vmraid import _
from vmraid.model.document import Document


class SanctionedLoanAmount(Document):
	def validate(self):
		sanctioned_doc = vmraid.db.exists(
			"Sanctioned Loan Amount", {"applicant": self.applicant, "company": self.company}
		)

		if sanctioned_doc and sanctioned_doc != self.name:
			vmraid.throw(
				_("Sanctioned Loan Amount already exists for {0} against company {1}").format(
					vmraid.bold(self.applicant), vmraid.bold(self.company)
				)
			)
