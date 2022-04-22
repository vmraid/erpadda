# Copyright (c) 2020, Wahni Green Technologies and Contributors
# License: GNU General Public License v3. See license.txt

import vmraid
from vmraid.custom.doctype.custom_field.custom_field import create_custom_fields
from vmraid.model.utils.rename_field import rename_field


def execute():
	company = vmraid.get_all("Company", filters={"country": "Saudi Arabia"})
	if not company:
		return

	if vmraid.db.exists("DocType", "Sales Invoice"):
		vmraid.reload_doc("accounts", "doctype", "sales_invoice", force=True)

		# rename_field method assumes that the field already exists or the doc is synced
		if not vmraid.db.has_column("Sales Invoice", "ksa_einv_qr"):
			create_custom_fields(
				{
					"Sales Invoice": [
						dict(
							fieldname="ksa_einv_qr",
							label="KSA E-Invoicing QR",
							fieldtype="Attach Image",
							read_only=1,
							no_copy=1,
							hidden=1,
						)
					]
				}
			)

		if vmraid.db.has_column("Sales Invoice", "qr_code"):
			rename_field("Sales Invoice", "qr_code", "ksa_einv_qr")
			vmraid.delete_doc_if_exists("Custom Field", "Sales Invoice-qr_code")
