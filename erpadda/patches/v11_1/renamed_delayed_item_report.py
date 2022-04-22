# Copyright (c) 2015, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid


def execute():
	for report in ["Delayed Order Item Summary", "Delayed Order Summary"]:
		if vmraid.db.exists("Report", report):
			vmraid.delete_doc("Report", report)
