# Copyright (c) 2019, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid

from erpadda.accounts.utils import check_and_delete_linked_reports


def execute():
	reports_to_delete = [
		"Requested Items To Be Ordered",
		"Purchase Order Items To Be Received or Billed",
		"Purchase Order Items To Be Received",
		"Purchase Order Items To Be Billed",
	]

	for report in reports_to_delete:
		if vmraid.db.exists("Report", report):
			delete_auto_email_reports(report)
			check_and_delete_linked_reports(report)

			vmraid.delete_doc("Report", report)


def delete_auto_email_reports(report):
	"""Check for one or multiple Auto Email Reports and delete"""
	auto_email_reports = vmraid.db.get_values("Auto Email Report", {"report": report}, ["name"])
	for auto_email_report in auto_email_reports:
		vmraid.delete_doc("Auto Email Report", auto_email_report[0])
