# Copyright (c) 2020, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt

import vmraid

from erpadda.regional.south_africa.setup import add_permissions, make_custom_fields


def execute():
	company = vmraid.get_all("Company", filters={"country": "South Africa"})
	if not company:
		return

	vmraid.reload_doc("regional", "doctype", "south_africa_vat_settings")
	vmraid.reload_doc("regional", "report", "vat_audit_report")
	vmraid.reload_doc("accounts", "doctype", "south_africa_vat_account")

	make_custom_fields()
	add_permissions()
