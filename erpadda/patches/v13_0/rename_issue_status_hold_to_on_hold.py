# Copyright (c) 2020, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid


def execute():
	if vmraid.db.exists("DocType", "Issue"):
		vmraid.reload_doc("support", "doctype", "issue")
		rename_status()


def rename_status():
	vmraid.db.sql(
		"""
		UPDATE
			`tabIssue`
		SET
			status = 'On Hold'
		WHERE
			status = 'Hold'
	"""
	)
