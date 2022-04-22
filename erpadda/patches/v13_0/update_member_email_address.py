# Copyright (c) 2020, VMRaid and Contributors
# MIT License. See license.txt


import vmraid
from vmraid.model.utils.rename_field import rename_field


def execute():
	"""add value to email_id column from email"""

	if vmraid.db.has_column("Member", "email"):
		# Get all members
		for member in vmraid.db.get_all("Member", pluck="name"):
			# Check if email_id already exists
			if not vmraid.db.get_value("Member", member, "email_id"):
				# fetch email id from the user linked field email
				email = vmraid.db.get_value("Member", member, "email")

				# Set the value for it
				vmraid.db.set_value("Member", member, "email_id", email)

	if vmraid.db.exists("DocType", "Membership Settings"):
		rename_field("Membership Settings", "enable_auto_invoicing", "enable_invoicing")
