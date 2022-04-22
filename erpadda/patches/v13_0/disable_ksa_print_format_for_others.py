# Copyright (c) 2020, Wahni Green Technologies and Contributors
# License: GNU General Public License v3. See license.txt

import vmraid

from erpadda.regional.saudi_arabia.setup import add_print_formats


def execute():
	company = vmraid.get_all("Company", filters={"country": "Saudi Arabia"})
	if company:
		add_print_formats()
		return

	if vmraid.db.exists("DocType", "Print Format"):
		vmraid.reload_doc("regional", "print_format", "ksa_vat_invoice", force=True)
		vmraid.reload_doc("regional", "print_format", "ksa_pos_invoice", force=True)
		for d in ("KSA VAT Invoice", "KSA POS Invoice"):
			vmraid.db.set_value("Print Format", d, "disabled", 1)
