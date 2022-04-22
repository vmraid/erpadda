// Copyright (c) 2016, VMRaid and contributors
// For license information, please see license.txt

vmraid.query_reports["Asset Depreciations and Balances"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": vmraid.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": vmraid.defaults.get_user_default("year_start_date"),
			"reqd": 1
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": vmraid.defaults.get_user_default("year_end_date"),
			"reqd": 1
		},
		{
			"fieldname":"asset_category",
			"label": __("Asset Category"),
			"fieldtype": "Link",
			"options": "Asset Category"
		}
	]
}
