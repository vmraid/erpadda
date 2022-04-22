# Copyright (c) 2019, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid

from erpadda.accounts.utils import check_and_delete_linked_reports


def execute():
	reports_to_delete = ["Ordered Items To Be Delivered", "Ordered Items To Be Billed"]

	for report in reports_to_delete:
		if vmraid.db.exists("Report", report):
			delete_links_from_desktop_icons(report)
			delete_auto_email_reports(report)
			check_and_delete_linked_reports(report)

			vmraid.delete_doc("Report", report)


def delete_auto_email_reports(report):
	"""Check for one or multiple Auto Email Reports and delete"""
	auto_email_reports = vmraid.db.get_values("Auto Email Report", {"report": report}, ["name"])
	for auto_email_report in auto_email_reports:
		vmraid.delete_doc("Auto Email Report", auto_email_report[0])


def delete_links_from_desktop_icons(report):
	"""Check for one or multiple Desktop Icons and delete"""
	desktop_icons = vmraid.db.get_values("Desktop Icon", {"_report": report}, ["name"])
	for desktop_icon in desktop_icons:
		vmraid.delete_doc("Desktop Icon", desktop_icon[0])
