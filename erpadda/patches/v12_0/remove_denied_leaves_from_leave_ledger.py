# Copyright (c) 2018, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid


def execute():
	"""Delete leave ledger entry created
	via leave applications with status != Approved"""
	if not vmraid.db.a_row_exists("Leave Ledger Entry"):
		return

	leave_application_list = get_denied_leave_application_list()
	if leave_application_list:
		delete_denied_leaves_from_leave_ledger_entry(leave_application_list)


def get_denied_leave_application_list():
	return vmraid.db.sql_list(
		""" Select name from `tabLeave Application` where status <> 'Approved' """
	)


def delete_denied_leaves_from_leave_ledger_entry(leave_application_list):
	if leave_application_list:
		vmraid.db.sql(
			""" Delete
			FROM `tabLeave Ledger Entry`
			WHERE
				transaction_type = 'Leave Application'
				AND transaction_name in (%s) """
			% (", ".join(["%s"] * len(leave_application_list))),  # nosec
			tuple(leave_application_list),
		)
