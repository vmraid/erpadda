# Copyright (c) 2015, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import copy

import vmraid
from vmraid import _
from vmraid.model.meta import get_field_precision
from vmraid.utils import cint, cstr, flt, formatdate, getdate, now

import erpadda
from erpadda.accounts.doctype.accounting_dimension.accounting_dimension import (
	get_accounting_dimensions,
)
from erpadda.accounts.doctype.budget.budget import validate_expense_against_budget


class ClosedAccountingPeriod(vmraid.ValidationError):
	pass


def make_gl_entries(
	gl_map,
	cancel=False,
	adv_adj=False,
	merge_entries=True,
	update_outstanding="Yes",
	from_repost=False,
):
	if gl_map:
		if not cancel:
			validate_accounting_period(gl_map)
			gl_map = process_gl_map(gl_map, merge_entries)
			if gl_map and len(gl_map) > 1:
				save_entries(gl_map, adv_adj, update_outstanding, from_repost)
			# Post GL Map proccess there may no be any GL Entries
			elif gl_map:
				vmraid.throw(
					_(
						"Incorrect number of General Ledger Entries found. You might have selected a wrong Account in the transaction."
					)
				)
		else:
			make_reverse_gl_entries(gl_map, adv_adj=adv_adj, update_outstanding=update_outstanding)


def validate_accounting_period(gl_map):
	accounting_periods = vmraid.db.sql(
		""" SELECT
			ap.name as name
		FROM
			`tabAccounting Period` ap, `tabClosed Document` cd
		WHERE
			ap.name = cd.parent
			AND ap.company = %(company)s
			AND cd.closed = 1
			AND cd.document_type = %(voucher_type)s
			AND %(date)s between ap.start_date and ap.end_date
			""",
		{
			"date": gl_map[0].posting_date,
			"company": gl_map[0].company,
			"voucher_type": gl_map[0].voucher_type,
		},
		as_dict=1,
	)

	if accounting_periods:
		vmraid.throw(
			_(
				"You cannot create or cancel any accounting entries with in the closed Accounting Period {0}"
			).format(vmraid.bold(accounting_periods[0].name)),
			ClosedAccountingPeriod,
		)


def process_gl_map(gl_map, merge_entries=True, precision=None):
	if not gl_map:
		return []

	gl_map = distribute_gl_based_on_cost_center_allocation(gl_map, precision)

	if merge_entries:
		gl_map = merge_similar_entries(gl_map, precision)

	gl_map = toggle_debit_credit_if_negative(gl_map)

	return gl_map


def distribute_gl_based_on_cost_center_allocation(gl_map, precision=None):
	cost_center_allocation = get_cost_center_allocation_data(
		gl_map[0]["company"], gl_map[0]["posting_date"]
	)
	if not cost_center_allocation:
		return gl_map

	new_gl_map = []
	for d in gl_map:
		cost_center = d.get("cost_center")
		if cost_center and cost_center_allocation.get(cost_center):
			for sub_cost_center, percentage in cost_center_allocation.get(cost_center, {}).items():
				gle = copy.deepcopy(d)
				gle.cost_center = sub_cost_center
				for field in ("debit", "credit", "debit_in_account_currency", "credit_in_company_currency"):
					gle[field] = flt(flt(d.get(field)) * percentage / 100, precision)
				new_gl_map.append(gle)
		else:
			new_gl_map.append(d)

	return new_gl_map


def get_cost_center_allocation_data(company, posting_date):
	par = vmraid.qb.DocType("Cost Center Allocation")
	child = vmraid.qb.DocType("Cost Center Allocation Percentage")

	records = (
		vmraid.qb.from_(par)
		.inner_join(child)
		.on(par.name == child.parent)
		.select(par.main_cost_center, child.cost_center, child.percentage)
		.where(par.docstatus == 1)
		.where(par.company == company)
		.where(par.valid_from <= posting_date)
		.orderby(par.valid_from, order=vmraid.qb.desc)
	).run(as_dict=True)

	cc_allocation = vmraid._dict()
	for d in records:
		cc_allocation.setdefault(d.main_cost_center, vmraid._dict()).setdefault(
			d.cost_center, d.percentage
		)

	return cc_allocation


def merge_similar_entries(gl_map, precision=None):
	merged_gl_map = []
	accounting_dimensions = get_accounting_dimensions()
	for entry in gl_map:
		# if there is already an entry in this account then just add it
		# to that entry
		same_head = check_if_in_list(entry, merged_gl_map, accounting_dimensions)
		if same_head:
			same_head.debit = flt(same_head.debit) + flt(entry.debit)
			same_head.debit_in_account_currency = flt(same_head.debit_in_account_currency) + flt(
				entry.debit_in_account_currency
			)
			same_head.credit = flt(same_head.credit) + flt(entry.credit)
			same_head.credit_in_account_currency = flt(same_head.credit_in_account_currency) + flt(
				entry.credit_in_account_currency
			)
		else:
			merged_gl_map.append(entry)

	company = gl_map[0].company if gl_map else erpadda.get_default_company()
	company_currency = erpadda.get_company_currency(company)

	if not precision:
		precision = get_field_precision(vmraid.get_meta("GL Entry").get_field("debit"), company_currency)

	# filter zero debit and credit entries
	merged_gl_map = filter(
		lambda x: flt(x.debit, precision) != 0 or flt(x.credit, precision) != 0, merged_gl_map
	)
	merged_gl_map = list(merged_gl_map)

	return merged_gl_map


def check_if_in_list(gle, gl_map, dimensions=None):
	account_head_fieldnames = [
		"voucher_detail_no",
		"party",
		"against_voucher",
		"cost_center",
		"against_voucher_type",
		"party_type",
		"project",
		"finance_book",
	]

	if dimensions:
		account_head_fieldnames = account_head_fieldnames + dimensions

	for e in gl_map:
		same_head = True
		if e.account != gle.account:
			same_head = False
			continue

		for fieldname in account_head_fieldnames:
			if cstr(e.get(fieldname)) != cstr(gle.get(fieldname)):
				same_head = False
				break

		if same_head:
			return e


def toggle_debit_credit_if_negative(gl_map):
	for entry in gl_map:
		# toggle debit, credit if negative entry
		if flt(entry.debit) < 0:
			entry.credit = flt(entry.credit) - flt(entry.debit)
			entry.debit = 0.0

		if flt(entry.debit_in_account_currency) < 0:
			entry.credit_in_account_currency = flt(entry.credit_in_account_currency) - flt(
				entry.debit_in_account_currency
			)
			entry.debit_in_account_currency = 0.0

		if flt(entry.credit) < 0:
			entry.debit = flt(entry.debit) - flt(entry.credit)
			entry.credit = 0.0

		if flt(entry.credit_in_account_currency) < 0:
			entry.debit_in_account_currency = flt(entry.debit_in_account_currency) - flt(
				entry.credit_in_account_currency
			)
			entry.credit_in_account_currency = 0.0

		update_net_values(entry)

	return gl_map


def update_net_values(entry):
	# In some scenarios net value needs to be shown in the ledger
	# This method updates net values as debit or credit
	if entry.post_net_value and entry.debit and entry.credit:
		if entry.debit > entry.credit:
			entry.debit = entry.debit - entry.credit
			entry.debit_in_account_currency = (
				entry.debit_in_account_currency - entry.credit_in_account_currency
			)
			entry.credit = 0
			entry.credit_in_account_currency = 0
		else:
			entry.credit = entry.credit - entry.debit
			entry.credit_in_account_currency = (
				entry.credit_in_account_currency - entry.debit_in_account_currency
			)

			entry.debit = 0
			entry.debit_in_account_currency = 0


def save_entries(gl_map, adv_adj, update_outstanding, from_repost=False):
	if not from_repost:
		validate_cwip_accounts(gl_map)

	process_debit_credit_difference(gl_map)

	if gl_map:
		check_freezing_date(gl_map[0]["posting_date"], adv_adj)

	for entry in gl_map:
		make_entry(entry, adv_adj, update_outstanding, from_repost)


def make_entry(args, adv_adj, update_outstanding, from_repost=False):
	gle = vmraid.new_doc("GL Entry")
	gle.update(args)
	gle.flags.ignore_permissions = 1
	gle.flags.from_repost = from_repost
	gle.flags.adv_adj = adv_adj
	gle.flags.update_outstanding = update_outstanding or "Yes"
	gle.submit()

	if not from_repost:
		validate_expense_against_budget(args)


def validate_cwip_accounts(gl_map):
	"""Validate that CWIP account are not used in Journal Entry"""
	if gl_map and gl_map[0].voucher_type != "Journal Entry":
		return

	cwip_enabled = any(
		cint(ac.enable_cwip_accounting)
		for ac in vmraid.db.get_all("Asset Category", "enable_cwip_accounting")
	)
	if cwip_enabled:
		cwip_accounts = [
			d[0]
			for d in vmraid.db.sql(
				"""select name from tabAccount
			where account_type = 'Capital Work in Progress' and is_group=0"""
			)
		]

		for entry in gl_map:
			if entry.account in cwip_accounts:
				vmraid.throw(
					_(
						"Account: <b>{0}</b> is capital Work in progress and can not be updated by Journal Entry"
					).format(entry.account)
				)


def process_debit_credit_difference(gl_map):
	precision = get_field_precision(
		vmraid.get_meta("GL Entry").get_field("debit"),
		currency=vmraid.get_cached_value("Company", gl_map[0].company, "default_currency"),
	)

	voucher_type = gl_map[0].voucher_type
	voucher_no = gl_map[0].voucher_no
	allowance = get_debit_credit_allowance(voucher_type, precision)

	debit_credit_diff = get_debit_credit_difference(gl_map, precision)
	if abs(debit_credit_diff) > allowance:
		raise_debit_credit_not_equal_error(debit_credit_diff, voucher_type, voucher_no)

	elif abs(debit_credit_diff) >= (1.0 / (10**precision)):
		make_round_off_gle(gl_map, debit_credit_diff, precision)

	debit_credit_diff = get_debit_credit_difference(gl_map, precision)
	if abs(debit_credit_diff) > allowance:
		raise_debit_credit_not_equal_error(debit_credit_diff, voucher_type, voucher_no)


def get_debit_credit_difference(gl_map, precision):
	debit_credit_diff = 0.0
	for entry in gl_map:
		entry.debit = flt(entry.debit, precision)
		entry.credit = flt(entry.credit, precision)
		debit_credit_diff += entry.debit - entry.credit

	debit_credit_diff = flt(debit_credit_diff, precision)

	return debit_credit_diff


def get_debit_credit_allowance(voucher_type, precision):
	if voucher_type in ("Journal Entry", "Payment Entry"):
		allowance = 5.0 / (10**precision)
	else:
		allowance = 0.5

	return allowance


def raise_debit_credit_not_equal_error(debit_credit_diff, voucher_type, voucher_no):
	vmraid.throw(
		_("Debit and Credit not equal for {0} #{1}. Difference is {2}.").format(
			voucher_type, voucher_no, debit_credit_diff
		)
	)


def make_round_off_gle(gl_map, debit_credit_diff, precision):
	round_off_account, round_off_cost_center = get_round_off_account_and_cost_center(
		gl_map[0].company
	)
	round_off_account_exists = False
	round_off_gle = vmraid._dict()
	for d in gl_map:
		if d.account == round_off_account:
			round_off_gle = d
			if d.debit:
				debit_credit_diff -= flt(d.debit)
			else:
				debit_credit_diff += flt(d.credit)
			round_off_account_exists = True

	if round_off_account_exists and abs(debit_credit_diff) < (1.0 / (10**precision)):
		gl_map.remove(round_off_gle)
		return

	if not round_off_gle:
		for k in ["voucher_type", "voucher_no", "company", "posting_date", "remarks"]:
			round_off_gle[k] = gl_map[0][k]

	round_off_gle.update(
		{
			"account": round_off_account,
			"debit_in_account_currency": abs(debit_credit_diff) if debit_credit_diff < 0 else 0,
			"credit_in_account_currency": debit_credit_diff if debit_credit_diff > 0 else 0,
			"debit": abs(debit_credit_diff) if debit_credit_diff < 0 else 0,
			"credit": debit_credit_diff if debit_credit_diff > 0 else 0,
			"cost_center": round_off_cost_center,
			"party_type": None,
			"party": None,
			"is_opening": "No",
			"against_voucher_type": None,
			"against_voucher": None,
		}
	)

	if not round_off_account_exists:
		gl_map.append(round_off_gle)


def get_round_off_account_and_cost_center(company):
	round_off_account, round_off_cost_center = vmraid.get_cached_value(
		"Company", company, ["round_off_account", "round_off_cost_center"]
	) or [None, None]
	if not round_off_account:
		vmraid.throw(_("Please mention Round Off Account in Company"))

	if not round_off_cost_center:
		vmraid.throw(_("Please mention Round Off Cost Center in Company"))

	return round_off_account, round_off_cost_center


def make_reverse_gl_entries(
	gl_entries=None, voucher_type=None, voucher_no=None, adv_adj=False, update_outstanding="Yes"
):
	"""
	Get original gl entries of the voucher
	and make reverse gl entries by swapping debit and credit
	"""

	if not gl_entries:
		gl_entry = vmraid.qb.DocType("GL Entry")
		gl_entries = (
			vmraid.qb.from_(gl_entry)
			.select("*")
			.where(gl_entry.voucher_type == voucher_type)
			.where(gl_entry.voucher_no == voucher_no)
			.where(gl_entry.is_cancelled == 0)
			.for_update()
		).run(as_dict=1)

	if gl_entries:
		validate_accounting_period(gl_entries)
		check_freezing_date(gl_entries[0]["posting_date"], adv_adj)
		set_as_cancel(gl_entries[0]["voucher_type"], gl_entries[0]["voucher_no"])

		for entry in gl_entries:
			new_gle = copy.deepcopy(entry)
			new_gle["name"] = None
			debit = new_gle.get("debit", 0)
			credit = new_gle.get("credit", 0)

			debit_in_account_currency = new_gle.get("debit_in_account_currency", 0)
			credit_in_account_currency = new_gle.get("credit_in_account_currency", 0)

			new_gle["debit"] = credit
			new_gle["credit"] = debit
			new_gle["debit_in_account_currency"] = credit_in_account_currency
			new_gle["credit_in_account_currency"] = debit_in_account_currency

			new_gle["remarks"] = "On cancellation of " + new_gle["voucher_no"]
			new_gle["is_cancelled"] = 1

			if new_gle["debit"] or new_gle["credit"]:
				make_entry(new_gle, adv_adj, "Yes")


def check_freezing_date(posting_date, adv_adj=False):
	"""
	Nobody can do GL Entries where posting date is before freezing date
	except authorized person

	Administrator has all the roles so this check will be bypassed if any role is allowed to post
	Hence stop admin to bypass if accounts are freezed
	"""
	if not adv_adj:
		acc_frozen_upto = vmraid.db.get_value("Accounts Settings", None, "acc_frozen_upto")
		if acc_frozen_upto:
			frozen_accounts_modifier = vmraid.db.get_value(
				"Accounts Settings", None, "frozen_accounts_modifier"
			)
			if getdate(posting_date) <= getdate(acc_frozen_upto) and (
				frozen_accounts_modifier not in vmraid.get_roles() or vmraid.session.user == "Administrator"
			):
				vmraid.throw(
					_("You are not authorized to add or update entries before {0}").format(
						formatdate(acc_frozen_upto)
					)
				)


def set_as_cancel(voucher_type, voucher_no):
	"""
	Set is_cancelled=1 in all original gl entries for the voucher
	"""
	vmraid.db.sql(
		"""UPDATE `tabGL Entry` SET is_cancelled = 1,
		modified=%s, modified_by=%s
		where voucher_type=%s and voucher_no=%s and is_cancelled = 0""",
		(now(), vmraid.session.user, voucher_type, voucher_no),
	)