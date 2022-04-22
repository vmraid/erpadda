# Copyright (c) 2019, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid


def execute():
	"""Move from due_advance_amount to pending_amount"""

	if vmraid.db.has_column("Employee Advance", "due_advance_amount"):
		vmraid.db.sql(""" UPDATE `tabEmployee Advance` SET pending_amount=due_advance_amount """)
