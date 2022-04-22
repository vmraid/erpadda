# Copyright (c) 2020, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid
from vmraid.model.utils.rename_field import rename_field


def execute():
	if vmraid.db.exists("DocType", "Issue"):
		issues = vmraid.db.get_all(
			"Issue",
			fields=["name", "response_by_variance", "resolution_by_variance", "mins_to_first_response"],
			order_by="creation desc",
		)
		vmraid.reload_doc("support", "doctype", "issue")

		# rename fields
		rename_map = {
			"agreement_fulfilled": "agreement_status",
			"mins_to_first_response": "first_response_time",
		}
		for old, new in rename_map.items():
			rename_field("Issue", old, new)

		# change fieldtype to duration
		count = 0
		for entry in issues:
			response_by_variance = convert_to_seconds(entry.response_by_variance, "Hours")
			resolution_by_variance = convert_to_seconds(entry.resolution_by_variance, "Hours")
			mins_to_first_response = convert_to_seconds(entry.mins_to_first_response, "Minutes")
			vmraid.db.set_value(
				"Issue",
				entry.name,
				{
					"response_by_variance": response_by_variance,
					"resolution_by_variance": resolution_by_variance,
					"first_response_time": mins_to_first_response,
				},
				update_modified=False,
			)
			# commit after every 100 updates
			count += 1
			if count % 100 == 0:
				vmraid.db.commit()

	if vmraid.db.exists("DocType", "Opportunity"):
		opportunities = vmraid.db.get_all(
			"Opportunity", fields=["name", "mins_to_first_response"], order_by="creation desc"
		)
		vmraid.reload_doctype("Opportunity", force=True)
		rename_field("Opportunity", "mins_to_first_response", "first_response_time")

		# change fieldtype to duration
		vmraid.reload_doc("crm", "doctype", "opportunity", force=True)
		count = 0
		for entry in opportunities:
			mins_to_first_response = convert_to_seconds(entry.mins_to_first_response, "Minutes")
			vmraid.db.set_value(
				"Opportunity", entry.name, "first_response_time", mins_to_first_response, update_modified=False
			)
			# commit after every 100 updates
			count += 1
			if count % 100 == 0:
				vmraid.db.commit()

	# renamed reports from "Minutes to First Response for Issues" to "First Response Time for Issues". Same for Opportunity
	for report in [
		"Minutes to First Response for Issues",
		"Minutes to First Response for Opportunity",
	]:
		if vmraid.db.exists("Report", report):
			vmraid.delete_doc("Report", report, ignore_permissions=True)


def convert_to_seconds(value, unit):
	seconds = 0
	if not value:
		return seconds
	if unit == "Hours":
		seconds = value * 3600
	if unit == "Minutes":
		seconds = value * 60
	return seconds
