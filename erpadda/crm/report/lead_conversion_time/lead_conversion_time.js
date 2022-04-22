// Copyright (c) 2018, VMRaid and contributors
// For license information, please see license.txt
/* eslint-disable */

vmraid.query_reports["Lead Conversion Time"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			'reqd': 1,
			"default": vmraid.datetime.add_days(vmraid.datetime.nowdate(), -30)
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			'reqd': 1,
			"default":vmraid.datetime.nowdate()
		},
	]
};
