# Copyright (c) 2019, VMRaid and contributors
# For license information, please see license.txt


import vmraid
from vmraid import _
from vmraid.model.document import Document

from erpadda.accounts.deferred_revenue import (
	build_conditions,
	convert_deferred_expense_to_expense,
	convert_deferred_revenue_to_income,
)
from erpadda.accounts.general_ledger import make_gl_entries


class ProcessDeferredAccounting(Document):
	def validate(self):
		if self.end_date < self.start_date:
			vmraid.throw(_("End date cannot be before start date"))

	def on_submit(self):
		conditions = build_conditions(self.type, self.account, self.company)
		if self.type == "Income":
			convert_deferred_revenue_to_income(self.name, self.start_date, self.end_date, conditions)
		else:
			convert_deferred_expense_to_expense(self.name, self.start_date, self.end_date, conditions)

	def on_cancel(self):
		self.ignore_linked_doctypes = ["GL Entry"]
		gl_entries = vmraid.get_all(
			"GL Entry",
			fields=["*"],
			filters={"against_voucher_type": self.doctype, "against_voucher": self.name},
		)

		make_gl_entries(gl_entries=gl_entries, cancel=1)
