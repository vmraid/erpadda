// Copyright (c) 2016, VMRaid and contributors
// For license information, please see license.txt
	vmraid.query_reports["Lead Owner Efficiency"] = {
		"filters": [
			{
				"fieldname": "from_date",
				"label": __("From Date"),
				"fieldtype": "Date",
				"default": vmraid.defaults.get_user_default("year_start_date"),
			},
			{
				"fieldname": "to_date",
				"label": __("To Date"),
				"fieldtype": "Date",
				"default": vmraid.defaults.get_user_default("year_end_date"),
			}
		]};
