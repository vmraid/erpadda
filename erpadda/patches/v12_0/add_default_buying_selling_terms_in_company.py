# Copyright (c) 2019, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid
from vmraid.model.utils.rename_field import rename_field


def execute():
	vmraid.reload_doc("setup", "doctype", "company")
	if vmraid.db.has_column("Company", "default_terms"):
		rename_field("Company", "default_terms", "default_selling_terms")

		for company in vmraid.get_all(
			"Company", ["name", "default_selling_terms", "default_buying_terms"]
		):
			if company.default_selling_terms and not company.default_buying_terms:
				vmraid.db.set_value(
					"Company", company.name, "default_buying_terms", company.default_selling_terms
				)

	vmraid.reload_doc("setup", "doctype", "terms_and_conditions")
	vmraid.db.sql("update `tabTerms and Conditions` set selling=1, buying=1, hr=1")
