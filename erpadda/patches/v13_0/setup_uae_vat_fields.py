# Copyright (c) 2019, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt

import vmraid

from erpadda.regional.united_arab_emirates.setup import setup


def execute():
	company = vmraid.get_all("Company", filters={"country": "United Arab Emirates"})
	if not company:
		return

	vmraid.reload_doc("regional", "report", "uae_vat_201")
	vmraid.reload_doc("regional", "doctype", "uae_vat_settings")
	vmraid.reload_doc("regional", "doctype", "uae_vat_account")

	setup()
