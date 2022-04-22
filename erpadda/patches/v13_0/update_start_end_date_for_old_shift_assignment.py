# Copyright (c) 2019, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid


def execute():
	vmraid.reload_doc("hr", "doctype", "shift_assignment")
	if vmraid.db.has_column("Shift Assignment", "date"):
		vmraid.db.sql(
			"""update `tabShift Assignment`
            set end_date=date, start_date=date
            where date IS NOT NULL and start_date IS NULL and end_date IS NULL;"""
		)
