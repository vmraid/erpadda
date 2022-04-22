// Copyright (c) 2015, VMRaid and Contributors
// License: GNU General Public License v3. See license.txt

vmraid.query_reports["Bank Reconciliation Statement"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"reqd": 1,
			"default": vmraid.defaults.get_user_default("Company")
		},
		{
			"fieldname":"account",
			"label": __("Bank Account"),
			"fieldtype": "Link",
			"options": "Account",
			"default": vmraid.defaults.get_user_default("Company")?
				locals[":Company"][vmraid.defaults.get_user_default("Company")]["default_bank_account"]: "",
			"reqd": 1,
			"get_query": function() {
				var company = vmraid.query_report.get_filter_value('company')
				return {
					"query": "erpadda.controllers.queries.get_account_list",
					"filters": [
						['Account', 'account_type', 'in', 'Bank, Cash'],
						['Account', 'is_group', '=', 0],
						['Account', 'disabled', '=', 0],
						['Account', 'company', '=', company],
					]
				}
			}
		},
		{
			"fieldname":"report_date",
			"label": __("Date"),
			"fieldtype": "Date",
			"default": vmraid.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname":"include_pos_transactions",
			"label": __("Include POS Transactions"),
			"fieldtype": "Check"
		},
	]
}
