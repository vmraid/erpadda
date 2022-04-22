# Copyright (c) 2019, VMRaid and contributors
# For license information, please see license.txt


import json
import math

import vmraid
from vmraid import _
from vmraid.model.document import Document
from vmraid.model.mapper import get_mapped_doc
from vmraid.utils import cint, flt, rounded

from erpadda.loan_management.doctype.loan.loan import (
	get_monthly_repayment_amount,
	get_sanctioned_amount_limit,
	get_total_loan_amount,
	validate_repayment_method,
)
from erpadda.loan_management.doctype.loan_security_price.loan_security_price import (
	get_loan_security_price,
)


class LoanApplication(Document):
	def validate(self):
		self.set_pledge_amount()
		self.set_loan_amount()
		self.validate_loan_amount()

		if self.is_term_loan:
			validate_repayment_method(
				self.repayment_method,
				self.loan_amount,
				self.repayment_amount,
				self.repayment_periods,
				self.is_term_loan,
			)

		self.validate_loan_type()

		self.get_repayment_details()
		self.check_sanctioned_amount_limit()

	def validate_loan_type(self):
		company = vmraid.get_value("Loan Type", self.loan_type, "company")
		if company != self.company:
			vmraid.throw(_("Please select Loan Type for company {0}").format(vmraid.bold(self.company)))

	def validate_loan_amount(self):
		if not self.loan_amount:
			vmraid.throw(_("Loan Amount is mandatory"))

		maximum_loan_limit = vmraid.db.get_value("Loan Type", self.loan_type, "maximum_loan_amount")
		if maximum_loan_limit and self.loan_amount > maximum_loan_limit:
			vmraid.throw(
				_("Loan Amount cannot exceed Maximum Loan Amount of {0}").format(maximum_loan_limit)
			)

		if self.maximum_loan_amount and self.loan_amount > self.maximum_loan_amount:
			vmraid.throw(
				_("Loan Amount exceeds maximum loan amount of {0} as per proposed securities").format(
					self.maximum_loan_amount
				)
			)

	def check_sanctioned_amount_limit(self):
		sanctioned_amount_limit = get_sanctioned_amount_limit(
			self.applicant_type, self.applicant, self.company
		)

		if sanctioned_amount_limit:
			total_loan_amount = get_total_loan_amount(self.applicant_type, self.applicant, self.company)

		if sanctioned_amount_limit and flt(self.loan_amount) + flt(total_loan_amount) > flt(
			sanctioned_amount_limit
		):
			vmraid.throw(
				_("Sanctioned Amount limit crossed for {0} {1}").format(
					self.applicant_type, vmraid.bold(self.applicant)
				)
			)

	def set_pledge_amount(self):
		for proposed_pledge in self.proposed_pledges:

			if not proposed_pledge.qty and not proposed_pledge.amount:
				vmraid.throw(_("Qty or Amount is mandatroy for loan security"))

			proposed_pledge.loan_security_price = get_loan_security_price(proposed_pledge.loan_security)

			if not proposed_pledge.qty:
				proposed_pledge.qty = cint(proposed_pledge.amount / proposed_pledge.loan_security_price)

			proposed_pledge.amount = proposed_pledge.qty * proposed_pledge.loan_security_price
			proposed_pledge.post_haircut_amount = cint(
				proposed_pledge.amount - (proposed_pledge.amount * proposed_pledge.haircut / 100)
			)

	def get_repayment_details(self):

		if self.is_term_loan:
			if self.repayment_method == "Repay Over Number of Periods":
				self.repayment_amount = get_monthly_repayment_amount(
					self.loan_amount, self.rate_of_interest, self.repayment_periods
				)

			if self.repayment_method == "Repay Fixed Amount per Period":
				monthly_interest_rate = flt(self.rate_of_interest) / (12 * 100)
				if monthly_interest_rate:
					min_repayment_amount = self.loan_amount * monthly_interest_rate
					if self.repayment_amount - min_repayment_amount <= 0:
						vmraid.throw(_("Repayment Amount must be greater than " + str(flt(min_repayment_amount, 2))))
					self.repayment_periods = math.ceil(
						(math.log(self.repayment_amount) - math.log(self.repayment_amount - min_repayment_amount))
						/ (math.log(1 + monthly_interest_rate))
					)
				else:
					self.repayment_periods = self.loan_amount / self.repayment_amount

			self.calculate_payable_amount()
		else:
			self.total_payable_amount = self.loan_amount

	def calculate_payable_amount(self):
		balance_amount = self.loan_amount
		self.total_payable_amount = 0
		self.total_payable_interest = 0

		while balance_amount > 0:
			interest_amount = rounded(balance_amount * flt(self.rate_of_interest) / (12 * 100))
			balance_amount = rounded(balance_amount + interest_amount - self.repayment_amount)

			self.total_payable_interest += interest_amount

		self.total_payable_amount = self.loan_amount + self.total_payable_interest

	def set_loan_amount(self):
		if self.is_secured_loan and not self.proposed_pledges:
			vmraid.throw(_("Proposed Pledges are mandatory for secured Loans"))

		if self.is_secured_loan and self.proposed_pledges:
			self.maximum_loan_amount = 0
			for security in self.proposed_pledges:
				self.maximum_loan_amount += flt(security.post_haircut_amount)

		if not self.loan_amount and self.is_secured_loan and self.proposed_pledges:
			self.loan_amount = self.maximum_loan_amount


@vmraid.whitelist()
def create_loan(source_name, target_doc=None, submit=0):
	def update_accounts(source_doc, target_doc, source_parent):
		account_details = vmraid.get_all(
			"Loan Type",
			fields=[
				"mode_of_payment",
				"payment_account",
				"loan_account",
				"interest_income_account",
				"penalty_income_account",
			],
			filters={"name": source_doc.loan_type},
		)[0]

		if source_doc.is_secured_loan:
			target_doc.maximum_loan_amount = 0

		target_doc.mode_of_payment = account_details.mode_of_payment
		target_doc.payment_account = account_details.payment_account
		target_doc.loan_account = account_details.loan_account
		target_doc.interest_income_account = account_details.interest_income_account
		target_doc.penalty_income_account = account_details.penalty_income_account
		target_doc.loan_application = source_name

	doclist = get_mapped_doc(
		"Loan Application",
		source_name,
		{
			"Loan Application": {
				"doctype": "Loan",
				"validation": {"docstatus": ["=", 1]},
				"postprocess": update_accounts,
			}
		},
		target_doc,
	)

	if submit:
		doclist.submit()

	return doclist


@vmraid.whitelist()
def create_pledge(loan_application, loan=None):
	loan_application_doc = vmraid.get_doc("Loan Application", loan_application)

	lsp = vmraid.new_doc("Loan Security Pledge")
	lsp.applicant_type = loan_application_doc.applicant_type
	lsp.applicant = loan_application_doc.applicant
	lsp.loan_application = loan_application_doc.name
	lsp.company = loan_application_doc.company

	if loan:
		lsp.loan = loan

	for pledge in loan_application_doc.proposed_pledges:

		lsp.append(
			"securities",
			{
				"loan_security": pledge.loan_security,
				"qty": pledge.qty,
				"loan_security_price": pledge.loan_security_price,
				"haircut": pledge.haircut,
			},
		)

	lsp.save()
	lsp.submit()

	message = _("Loan Security Pledge Created : {0}").format(lsp.name)
	vmraid.msgprint(message)

	return lsp.name


# This is a sandbox method to get the proposed pledges
@vmraid.whitelist()
def get_proposed_pledge(securities):
	if isinstance(securities, str):
		securities = json.loads(securities)

	proposed_pledges = {"securities": []}
	maximum_loan_amount = 0

	for security in securities:
		security = vmraid._dict(security)
		if not security.qty and not security.amount:
			vmraid.throw(_("Qty or Amount is mandatroy for loan security"))

		security.loan_security_price = get_loan_security_price(security.loan_security)

		if not security.qty:
			security.qty = cint(security.amount / security.loan_security_price)

		security.amount = security.qty * security.loan_security_price
		security.post_haircut_amount = cint(security.amount - (security.amount * security.haircut / 100))

		maximum_loan_amount += security.post_haircut_amount

		proposed_pledges["securities"].append(security)

	proposed_pledges["maximum_loan_amount"] = maximum_loan_amount

	return proposed_pledges
