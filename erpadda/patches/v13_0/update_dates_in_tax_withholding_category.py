# Copyright (c) 2021, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt

import vmraid


def execute():
	vmraid.reload_doc("accounts", "doctype", "Tax Withholding Rate")

	if vmraid.db.has_column("Tax Withholding Rate", "fiscal_year"):
		tds_category_rates = vmraid.get_all("Tax Withholding Rate", fields=["name", "fiscal_year"])

		fiscal_year_map = {}
		fiscal_year_details = vmraid.get_all(
			"Fiscal Year", fields=["name", "year_start_date", "year_end_date"]
		)

		for d in fiscal_year_details:
			fiscal_year_map.setdefault(d.name, d)

		for rate in tds_category_rates:
			from_date = fiscal_year_map.get(rate.fiscal_year).get("year_start_date")
			to_date = fiscal_year_map.get(rate.fiscal_year).get("year_end_date")

			vmraid.db.set_value(
				"Tax Withholding Rate", rate.name, {"from_date": from_date, "to_date": to_date}
			)
