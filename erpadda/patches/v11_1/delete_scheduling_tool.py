# Copyright (c) 2015, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid


def execute():
	if vmraid.db.exists("DocType", "Scheduling Tool"):
		vmraid.delete_doc("DocType", "Scheduling Tool", ignore_permissions=True)
