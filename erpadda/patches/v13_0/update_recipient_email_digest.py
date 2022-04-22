# Copyright (c) 2020, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid


def execute():
	vmraid.reload_doc("setup", "doctype", "Email Digest")
	vmraid.reload_doc("setup", "doctype", "Email Digest Recipient")
	email_digests = vmraid.db.get_list("Email Digest", fields=["name", "recipient_list"])
	for email_digest in email_digests:
		if email_digest.recipient_list:
			for recipient in email_digest.recipient_list.split("\n"):
				doc = vmraid.get_doc(
					{
						"doctype": "Email Digest Recipient",
						"parenttype": "Email Digest",
						"parentfield": "recipients",
						"parent": email_digest.name,
						"recipient": recipient,
					}
				)
				doc.insert()
