# Copyright (c) 2018, VMRaid and contributors
# For license information, please see license.txt


import vmraid
from vmraid import _
from vmraid.utils import flt, get_datetime

from erpadda.accounts.doctype.pos_invoice_merge_log.pos_invoice_merge_log import (
	consolidate_pos_invoices,
	unconsolidate_pos_invoices,
)
from erpadda.controllers.status_updater import StatusUpdater


class POSClosingEntry(StatusUpdater):
	def validate(self):
		if vmraid.db.get_value("POS Opening Entry", self.pos_opening_entry, "status") != "Open":
			vmraid.throw(_("Selected POS Opening Entry should be open."), title=_("Invalid Opening Entry"))

		self.validate_pos_invoices()

	def validate_pos_invoices(self):
		invalid_rows = []
		for d in self.pos_transactions:
			invalid_row = {"idx": d.idx}
			pos_invoice = vmraid.db.get_values(
				"POS Invoice",
				d.pos_invoice,
				["consolidated_invoice", "pos_profile", "docstatus", "owner"],
				as_dict=1,
			)[0]
			if pos_invoice.consolidated_invoice:
				invalid_row.setdefault("msg", []).append(
					_("POS Invoice is {}").format(vmraid.bold("already consolidated"))
				)
				invalid_rows.append(invalid_row)
				continue
			if pos_invoice.pos_profile != self.pos_profile:
				invalid_row.setdefault("msg", []).append(
					_("POS Profile doesn't matches {}").format(vmraid.bold(self.pos_profile))
				)
			if pos_invoice.docstatus != 1:
				invalid_row.setdefault("msg", []).append(
					_("POS Invoice is not {}").format(vmraid.bold("submitted"))
				)
			if pos_invoice.owner != self.user:
				invalid_row.setdefault("msg", []).append(
					_("POS Invoice isn't created by user {}").format(vmraid.bold(self.owner))
				)

			if invalid_row.get("msg"):
				invalid_rows.append(invalid_row)

		if not invalid_rows:
			return

		error_list = []
		for row in invalid_rows:
			for msg in row.get("msg"):
				error_list.append(_("Row #{}: {}").format(row.get("idx"), msg))

		vmraid.throw(error_list, title=_("Invalid POS Invoices"), as_list=True)

	@vmraid.whitelist()
	def get_payment_reconciliation_details(self):
		currency = vmraid.get_cached_value("Company", self.company, "default_currency")
		return vmraid.render_template(
			"erpadda/accounts/doctype/pos_closing_entry/closing_voucher_details.html",
			{"data": self, "currency": currency},
		)

	def on_submit(self):
		consolidate_pos_invoices(closing_entry=self)

	def on_cancel(self):
		unconsolidate_pos_invoices(closing_entry=self)

	@vmraid.whitelist()
	def retry(self):
		consolidate_pos_invoices(closing_entry=self)

	def update_opening_entry(self, for_cancel=False):
		opening_entry = vmraid.get_doc("POS Opening Entry", self.pos_opening_entry)
		opening_entry.pos_closing_entry = self.name if not for_cancel else None
		opening_entry.set_status()
		opening_entry.save()


@vmraid.whitelist()
@vmraid.validate_and_sanitize_search_inputs
def get_cashiers(doctype, txt, searchfield, start, page_len, filters):
	cashiers_list = vmraid.get_all("POS Profile User", filters=filters, fields=["user"], as_list=1)
	return [c for c in cashiers_list]


@vmraid.whitelist()
def get_pos_invoices(start, end, pos_profile, user):
	data = vmraid.db.sql(
		"""
	select
		name, timestamp(posting_date, posting_time) as "timestamp"
	from
		`tabPOS Invoice`
	where
		owner = %s and docstatus = 1 and pos_profile = %s and ifnull(consolidated_invoice,'') = ''
	""",
		(user, pos_profile),
		as_dict=1,
	)

	data = list(
		filter(lambda d: get_datetime(start) <= get_datetime(d.timestamp) <= get_datetime(end), data)
	)
	# need to get taxes and payments so can't avoid get_doc
	data = [vmraid.get_doc("POS Invoice", d.name).as_dict() for d in data]

	return data


def make_closing_entry_from_opening(opening_entry):
	closing_entry = vmraid.new_doc("POS Closing Entry")
	closing_entry.pos_opening_entry = opening_entry.name
	closing_entry.period_start_date = opening_entry.period_start_date
	closing_entry.period_end_date = vmraid.utils.get_datetime()
	closing_entry.pos_profile = opening_entry.pos_profile
	closing_entry.user = opening_entry.user
	closing_entry.company = opening_entry.company
	closing_entry.grand_total = 0
	closing_entry.net_total = 0
	closing_entry.total_quantity = 0

	invoices = get_pos_invoices(
		closing_entry.period_start_date,
		closing_entry.period_end_date,
		closing_entry.pos_profile,
		closing_entry.user,
	)

	pos_transactions = []
	taxes = []
	payments = []
	for detail in opening_entry.balance_details:
		payments.append(
			vmraid._dict(
				{
					"mode_of_payment": detail.mode_of_payment,
					"opening_amount": detail.opening_amount,
					"expected_amount": detail.opening_amount,
				}
			)
		)

	for d in invoices:
		pos_transactions.append(
			vmraid._dict(
				{
					"pos_invoice": d.name,
					"posting_date": d.posting_date,
					"grand_total": d.grand_total,
					"customer": d.customer,
				}
			)
		)
		closing_entry.grand_total += flt(d.grand_total)
		closing_entry.net_total += flt(d.net_total)
		closing_entry.total_quantity += flt(d.total_qty)

		for t in d.taxes:
			existing_tax = [tx for tx in taxes if tx.account_head == t.account_head and tx.rate == t.rate]
			if existing_tax:
				existing_tax[0].amount += flt(t.tax_amount)
			else:
				taxes.append(
					vmraid._dict({"account_head": t.account_head, "rate": t.rate, "amount": t.tax_amount})
				)

		for p in d.payments:
			existing_pay = [pay for pay in payments if pay.mode_of_payment == p.mode_of_payment]
			if existing_pay:
				existing_pay[0].expected_amount += flt(p.amount)
			else:
				payments.append(
					vmraid._dict(
						{"mode_of_payment": p.mode_of_payment, "opening_amount": 0, "expected_amount": p.amount}
					)
				)

	closing_entry.set("pos_transactions", pos_transactions)
	closing_entry.set("payment_reconciliation", payments)
	closing_entry.set("taxes", taxes)

	return closing_entry
