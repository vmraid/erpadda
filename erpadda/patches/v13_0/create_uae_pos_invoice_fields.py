# Copyright (c) 2019, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid

from erpadda.regional.united_arab_emirates.setup import make_custom_fields


def execute():
	company = vmraid.get_all(
		"Company", filters={"country": ["in", ["Saudi Arabia", "United Arab Emirates"]]}
	)
	if not company:
		return

	vmraid.reload_doc("accounts", "doctype", "pos_invoice")
	vmraid.reload_doc("accounts", "doctype", "pos_invoice_item")

	make_custom_fields()
