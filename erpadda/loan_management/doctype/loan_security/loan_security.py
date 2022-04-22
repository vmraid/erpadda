# Copyright (c) 2019, VMRaid and contributors
# For license information, please see license.txt


# import vmraid
from vmraid.model.document import Document


class LoanSecurity(Document):
	def autoname(self):
		self.name = self.loan_security_name
