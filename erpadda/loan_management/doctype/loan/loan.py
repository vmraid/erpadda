# Copyright (c) 2019, VMRaid and contributors
# For license information, please see license.txt


import json
import math

import vmraid
from vmraid import _
from vmraid.utils import add_months, flt, get_last_day, getdate, now_datetime, nowdate

import erpadda
from erpadda.accounts.doctype.journal_entry.journal_entry import get_payment_entry
from erpadda.controllers.accounts_controller import AccountsController
from erpadda.loan_management.doctype.loan_repayment.loan_repayment import calculate_amounts
from erpadda.loan_management.doctype.loan_security_unpledge.loan_security_unpledge import (
	get_pledged_security_qty,
)


class Loan(AccountsController):
	def validate(self):
		if self.applicant_type == "Employee" and self.repay_from_salary:
			validate_employee_currency_with_company_currency(self.applicant, self.company)
		self.set_loan_amount()
		self.validate_loan_amount()
		self.set_missing_fields()
		self.validate_cost_center()
		self.validate_accounts()
		self.check_sanctioned_amount_limit()
		self.validate_repay_from_salary()

		if self.is_term_loan:
			validate_repayment_method(
				self.repayment_method,
				self.loan_amount,
				self.monthly_repayment_amount,
				self.repayment_periods,
				self.is_term_loan,
			)
			self.make_repayment_schedule()
			self.set_repayment_period()

		self.calculate_totals()

	def validate_accounts(self):
		for fieldname in [
			"payment_account",
			"loan_account",
			"interest_income_account",
			"penalty_income_account",
		]:
			company = vmraid.get_value("Account", self.get(fieldname), "company")

			if company != self.company:
				vmraid.throw(
					_("Account {0} does not belongs to company {1}").format(
						vmraid.bold(self.get(fieldname)), vmraid.bold(self.company)
					)
				)

	def validate_cost_center(self):
		if not self.cost_center and self.rate_of_interest != 0:
			self.cost_center = vmraid.db.get_value("Company", self.company, "cost_center")

		if not self.cost_center:
			vmraid.throw(_("Cost center is mandatory for loans having rate of interest greater than 0"))

	def on_submit(self):
		self.link_loan_security_pledge()

	def on_cancel(self):
		self.unlink_loan_security_pledge()
		self.ignore_linked_doctypes = ["GL Entry"]

	def set_missing_fields(self):
		if not self.company:
			self.company = erpadda.get_default_company()

		if not self.posting_date:
			self.posting_date = nowdate()

		if self.loan_type and not self.rate_of_interest:
			self.rate_of_interest = vmraid.db.get_value("Loan Type", self.loan_type, "rate_of_interest")

		if self.repayment_method == "Repay Over Number of Periods":
			self.monthly_repayment_amount = get_monthly_repayment_amount(
				self.loan_amount, self.rate_of_interest, self.repayment_periods
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

	def validate_repay_from_salary(self):
		if not self.is_term_loan and self.repay_from_salary:
			vmraid.throw(_("Repay From Salary can be selected only for term loans"))

	def make_repayment_schedule(self):
		if not self.repayment_start_date:
			vmraid.throw(_("Repayment Start Date is mandatory for term loans"))

		self.repayment_schedule = []
		payment_date = self.repayment_start_date
		balance_amount = self.loan_amount
		while balance_amount > 0:
			interest_amount = flt(balance_amount * flt(self.rate_of_interest) / (12 * 100))
			principal_amount = self.monthly_repayment_amount - interest_amount
			balance_amount = flt(balance_amount + interest_amount - self.monthly_repayment_amount)
			if balance_amount < 0:
				principal_amount += balance_amount
				balance_amount = 0.0

			total_payment = principal_amount + interest_amount
			self.append(
				"repayment_schedule",
				{
					"payment_date": payment_date,
					"principal_amount": principal_amount,
					"interest_amount": interest_amount,
					"total_payment": total_payment,
					"balance_loan_amount": balance_amount,
				},
			)
			next_payment_date = add_single_month(payment_date)
			payment_date = next_payment_date

	def set_repayment_period(self):
		if self.repayment_method == "Repay Fixed Amount per Period":
			repayment_periods = len(self.repayment_schedule)

			self.repayment_periods = repayment_periods

	def calculate_totals(self):
		self.total_payment = 0
		self.total_interest_payable = 0
		self.total_amount_paid = 0

		if self.is_term_loan:
			for data in self.repayment_schedule:
				self.total_payment += data.total_payment
				self.total_interest_payable += data.interest_amount
		else:
			self.total_payment = self.loan_amount

	def set_loan_amount(self):
		if self.loan_application and not self.loan_amount:
			self.loan_amount = vmraid.db.get_value("Loan Application", self.loan_application, "loan_amount")

	def validate_loan_amount(self):
		if self.maximum_loan_amount and self.loan_amount > self.maximum_loan_amount:
			msg = _("Loan amount cannot be greater than {0}").format(self.maximum_loan_amount)
			vmraid.throw(msg)

		if not self.loan_amount:
			vmraid.throw(_("Loan amount is mandatory"))

	def link_loan_security_pledge(self):
		if self.is_secured_loan and self.loan_application:
			maximum_loan_value = vmraid.db.get_value(
				"Loan Security Pledge",
				{"loan_application": self.loan_application, "status": "Requested"},
				"sum(maximum_loan_value)",
			)

			if maximum_loan_value:
				vmraid.db.sql(
					"""
					UPDATE `tabLoan Security Pledge`
					SET loan = %s, pledge_time = %s, status = 'Pledged'
					WHERE status = 'Requested' and loan_application = %s
				""",
					(self.name, now_datetime(), self.loan_application),
				)

				self.db_set("maximum_loan_amount", maximum_loan_value)

	def unlink_loan_security_pledge(self):
		pledges = vmraid.get_all("Loan Security Pledge", fields=["name"], filters={"loan": self.name})
		pledge_list = [d.name for d in pledges]
		if pledge_list:
			vmraid.db.sql(
				"""UPDATE `tabLoan Security Pledge` SET
				loan = '', status = 'Unpledged'
				where name in (%s) """
				% (", ".join(["%s"] * len(pledge_list))),
				tuple(pledge_list),
			)  # nosec


def update_total_amount_paid(doc):
	total_amount_paid = 0
	for data in doc.repayment_schedule:
		if data.paid:
			total_amount_paid += data.total_payment
	vmraid.db.set_value("Loan", doc.name, "total_amount_paid", total_amount_paid)


def get_total_loan_amount(applicant_type, applicant, company):
	pending_amount = 0
	loan_details = vmraid.db.get_all(
		"Loan",
		filters={
			"applicant_type": applicant_type,
			"company": company,
			"applicant": applicant,
			"docstatus": 1,
			"status": ("!=", "Closed"),
		},
		fields=[
			"status",
			"total_payment",
			"disbursed_amount",
			"total_interest_payable",
			"total_principal_paid",
			"written_off_amount",
		],
	)

	interest_amount = flt(
		vmraid.db.get_value(
			"Loan Interest Accrual",
			{"applicant_type": applicant_type, "company": company, "applicant": applicant, "docstatus": 1},
			"sum(interest_amount - paid_interest_amount)",
		)
	)

	for loan in loan_details:
		if loan.status in ("Disbursed", "Loan Closure Requested"):
			pending_amount += (
				flt(loan.total_payment)
				- flt(loan.total_interest_payable)
				- flt(loan.total_principal_paid)
				- flt(loan.written_off_amount)
			)
		elif loan.status == "Partially Disbursed":
			pending_amount += (
				flt(loan.disbursed_amount)
				- flt(loan.total_interest_payable)
				- flt(loan.total_principal_paid)
				- flt(loan.written_off_amount)
			)
		elif loan.status == "Sanctioned":
			pending_amount += flt(loan.total_payment)

	pending_amount += interest_amount

	return pending_amount


def get_sanctioned_amount_limit(applicant_type, applicant, company):
	return vmraid.db.get_value(
		"Sanctioned Loan Amount",
		{"applicant_type": applicant_type, "company": company, "applicant": applicant},
		"sanctioned_amount_limit",
	)


def validate_repayment_method(
	repayment_method, loan_amount, monthly_repayment_amount, repayment_periods, is_term_loan
):

	if is_term_loan and not repayment_method:
		vmraid.throw(_("Repayment Method is mandatory for term loans"))

	if repayment_method == "Repay Over Number of Periods" and not repayment_periods:
		vmraid.throw(_("Please enter Repayment Periods"))

	if repayment_method == "Repay Fixed Amount per Period":
		if not monthly_repayment_amount:
			vmraid.throw(_("Please enter repayment Amount"))
		if monthly_repayment_amount > loan_amount:
			vmraid.throw(_("Monthly Repayment Amount cannot be greater than Loan Amount"))


def get_monthly_repayment_amount(loan_amount, rate_of_interest, repayment_periods):
	if rate_of_interest:
		monthly_interest_rate = flt(rate_of_interest) / (12 * 100)
		monthly_repayment_amount = math.ceil(
			(loan_amount * monthly_interest_rate * (1 + monthly_interest_rate) ** repayment_periods)
			/ ((1 + monthly_interest_rate) ** repayment_periods - 1)
		)
	else:
		monthly_repayment_amount = math.ceil(flt(loan_amount) / repayment_periods)
	return monthly_repayment_amount


@vmraid.whitelist()
def request_loan_closure(loan, posting_date=None):
	if not posting_date:
		posting_date = getdate()

	amounts = calculate_amounts(loan, posting_date)
	pending_amount = (
		amounts["pending_principal_amount"]
		+ amounts["unaccrued_interest"]
		+ amounts["interest_amount"]
		+ amounts["penalty_amount"]
	)

	loan_type = vmraid.get_value("Loan", loan, "loan_type")
	write_off_limit = vmraid.get_value("Loan Type", loan_type, "write_off_amount")

	if pending_amount and abs(pending_amount) < write_off_limit:
		# Auto create loan write off and update status as loan closure requested
		write_off = make_loan_write_off(loan)
		write_off.submit()
	elif pending_amount > 0:
		vmraid.throw(_("Cannot close loan as there is an outstanding of {0}").format(pending_amount))

	vmraid.db.set_value("Loan", loan, "status", "Loan Closure Requested")


@vmraid.whitelist()
def get_loan_application(loan_application):
	loan = vmraid.get_doc("Loan Application", loan_application)
	if loan:
		return loan.as_dict()


def close_loan(loan, total_amount_paid):
	vmraid.db.set_value("Loan", loan, "total_amount_paid", total_amount_paid)
	vmraid.db.set_value("Loan", loan, "status", "Closed")


@vmraid.whitelist()
def make_loan_disbursement(loan, company, applicant_type, applicant, pending_amount=0, as_dict=0):
	disbursement_entry = vmraid.new_doc("Loan Disbursement")
	disbursement_entry.against_loan = loan
	disbursement_entry.applicant_type = applicant_type
	disbursement_entry.applicant = applicant
	disbursement_entry.company = company
	disbursement_entry.disbursement_date = nowdate()
	disbursement_entry.posting_date = nowdate()

	disbursement_entry.disbursed_amount = pending_amount
	if as_dict:
		return disbursement_entry.as_dict()
	else:
		return disbursement_entry


@vmraid.whitelist()
def make_repayment_entry(loan, applicant_type, applicant, loan_type, company, as_dict=0):
	repayment_entry = vmraid.new_doc("Loan Repayment")
	repayment_entry.against_loan = loan
	repayment_entry.applicant_type = applicant_type
	repayment_entry.applicant = applicant
	repayment_entry.company = company
	repayment_entry.loan_type = loan_type
	repayment_entry.posting_date = nowdate()

	if as_dict:
		return repayment_entry.as_dict()
	else:
		return repayment_entry


@vmraid.whitelist()
def make_loan_write_off(loan, company=None, posting_date=None, amount=0, as_dict=0):
	if not company:
		company = vmraid.get_value("Loan", loan, "company")

	if not posting_date:
		posting_date = getdate()

	amounts = calculate_amounts(loan, posting_date)
	pending_amount = amounts["pending_principal_amount"]

	if amount and (amount > pending_amount):
		vmraid.throw(_("Write Off amount cannot be greater than pending loan amount"))

	if not amount:
		amount = pending_amount

	# get default write off account from company master
	write_off_account = vmraid.get_value("Company", company, "write_off_account")

	write_off = vmraid.new_doc("Loan Write Off")
	write_off.loan = loan
	write_off.posting_date = posting_date
	write_off.write_off_account = write_off_account
	write_off.write_off_amount = amount
	write_off.save()

	if as_dict:
		return write_off.as_dict()
	else:
		return write_off


@vmraid.whitelist()
def unpledge_security(
	loan=None, loan_security_pledge=None, security_map=None, as_dict=0, save=0, submit=0, approve=0
):
	# if no security_map is passed it will be considered as full unpledge
	if security_map and isinstance(security_map, str):
		security_map = json.loads(security_map)

	if loan:
		pledge_qty_map = security_map or get_pledged_security_qty(loan)
		loan_doc = vmraid.get_doc("Loan", loan)
		unpledge_request = create_loan_security_unpledge(
			pledge_qty_map, loan_doc.name, loan_doc.company, loan_doc.applicant_type, loan_doc.applicant
		)
	# will unpledge qty based on loan security pledge
	elif loan_security_pledge:
		security_map = {}
		pledge_doc = vmraid.get_doc("Loan Security Pledge", loan_security_pledge)
		for security in pledge_doc.securities:
			security_map.setdefault(security.loan_security, security.qty)

		unpledge_request = create_loan_security_unpledge(
			security_map,
			pledge_doc.loan,
			pledge_doc.company,
			pledge_doc.applicant_type,
			pledge_doc.applicant,
		)

	if save:
		unpledge_request.save()

	if submit:
		unpledge_request.submit()

	if approve:
		if unpledge_request.docstatus == 1:
			unpledge_request.status = "Approved"
			unpledge_request.save()
		else:
			vmraid.throw(_("Only submittted unpledge requests can be approved"))

	if as_dict:
		return unpledge_request
	else:
		return unpledge_request


def create_loan_security_unpledge(unpledge_map, loan, company, applicant_type, applicant):
	unpledge_request = vmraid.new_doc("Loan Security Unpledge")
	unpledge_request.applicant_type = applicant_type
	unpledge_request.applicant = applicant
	unpledge_request.loan = loan
	unpledge_request.company = company

	for security, qty in unpledge_map.items():
		if qty:
			unpledge_request.append("securities", {"loan_security": security, "qty": qty})

	return unpledge_request


def validate_employee_currency_with_company_currency(applicant, company):
	from erpadda.payroll.doctype.salary_structure_assignment.salary_structure_assignment import (
		get_employee_currency,
	)

	if not applicant:
		vmraid.throw(_("Please select Applicant"))
	if not company:
		vmraid.throw(_("Please select Company"))
	employee_currency = get_employee_currency(applicant)
	company_currency = erpadda.get_company_currency(company)
	if employee_currency != company_currency:
		vmraid.throw(
			_(
				"Loan cannot be repayed from salary for Employee {0} because salary is processed in currency {1}"
			).format(applicant, employee_currency)
		)


@vmraid.whitelist()
def get_shortfall_applicants():
	loans = vmraid.get_all("Loan Security Shortfall", {"status": "Pending"}, pluck="loan")
	applicants = set(vmraid.get_all("Loan", {"name": ("in", loans)}, pluck="name"))

	return {"value": len(applicants), "fieldtype": "Int"}


def add_single_month(date):
	if getdate(date) == get_last_day(date):
		return get_last_day(add_months(date, 1))
	else:
		return add_months(date, 1)


@vmraid.whitelist()
def make_refund_jv(loan, amount=0, reference_number=None, reference_date=None, submit=0):
	loan_details = vmraid.db.get_value(
		"Loan",
		loan,
		[
			"applicant_type",
			"applicant",
			"loan_account",
			"payment_account",
			"posting_date",
			"company",
			"name",
			"total_payment",
			"total_principal_paid",
		],
		as_dict=1,
	)

	loan_details.doctype = "Loan"
	loan_details[loan_details.applicant_type.lower()] = loan_details.applicant

	if not amount:
		amount = flt(loan_details.total_principal_paid - loan_details.total_payment)

		if amount < 0:
			vmraid.throw(_("No excess amount pending for refund"))

	refund_jv = get_payment_entry(
		loan_details,
		{
			"party_type": loan_details.applicant_type,
			"party_account": loan_details.loan_account,
			"amount_field_party": "debit_in_account_currency",
			"amount_field_bank": "credit_in_account_currency",
			"amount": amount,
			"bank_account": loan_details.payment_account,
		},
	)

	if reference_number:
		refund_jv.cheque_no = reference_number

	if reference_date:
		refund_jv.cheque_date = reference_date

	if submit:
		refund_jv.submit()

	return refund_jv
