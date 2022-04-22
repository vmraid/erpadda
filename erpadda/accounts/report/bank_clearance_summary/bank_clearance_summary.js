// Copyright (c) 2015, VMRaid and Contributors
// License: GNU General Public License v3. See license.txt

vmraid.query_reports["Bank Clearance Summary"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": vmraid.defaults.get_user_default("year_start_date"),
			"width": "80"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": vmraid.datetime.get_today()
		},
		{
			"fieldname":"account",
			"label": __("Bank Account"),
			"fieldtype": "Link",
			"options": "Account",
			"reqd": 1,
			"default": vmraid.defaults.get_user_default("Company")?
				locals[":Company"][vmraid.defaults.get_user_default("Company")]["default_bank_account"]: "",
			"get_query": function() {
				return {
					"query": "erpadda.controllers.queries.get_account_list",
					"filters": [
						['Account', 'account_type', 'in', 'Bank, Cash'],
						['Account', 'is_group', '=', 0],
					]
				}
			}
		},
	]
}
