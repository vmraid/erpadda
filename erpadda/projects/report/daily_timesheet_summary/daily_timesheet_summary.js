// Copyright (c) 2016, VMRaid and contributors
// For license information, please see license.txt

vmraid.query_reports["Daily Timesheet Summary"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": vmraid.datetime.get_today()
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": vmraid.datetime.get_today()
		},
	]
}
