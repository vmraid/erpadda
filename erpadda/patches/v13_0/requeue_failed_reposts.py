import vmraid
from vmraid.utils import cstr


def execute():

	reposts = vmraid.get_all(
		"Repost Item Valuation",
		{"status": "Failed", "modified": [">", "2021-10-05"]},
		["name", "modified", "error_log"],
	)

	for repost in reposts:
		if "check_freezing_date" in cstr(repost.error_log):
			vmraid.db.set_value("Repost Item Valuation", repost.name, "status", "Queued")
