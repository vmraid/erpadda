// Copyright (c) 2015, VMRaid and Contributors
// License: GNU General Public License v3. See license.txt
vmraid.query_reports["Sales Payment Summary"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": vmraid.datetime.get_today(),
			"reqd": 1,
			"width": "80"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": vmraid.datetime.get_today()
		},
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": vmraid.defaults.get_user_default("Company")
		},
		{
			"fieldname":"owner",
			"label": __("Owner"),
			"fieldtype": "Link",
			"options": "User",
			"defaults": user
		},
		{
			"fieldname":"is_pos",
			"label": __("Show only POS"),
			"fieldtype": "Check"
		},
		{
			"fieldname":"payment_detail",
			"label": __("Show Payment Details"),
			"fieldtype": "Check"
		},
	]
};
