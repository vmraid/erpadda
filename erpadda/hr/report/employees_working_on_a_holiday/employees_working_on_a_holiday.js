// Copyright (c) 2016, VMRaid and contributors
// For license information, please see license.txt

vmraid.query_reports["Employees working on a holiday"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": vmraid.datetime.year_start()
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": vmraid.datetime.year_end()
		},
		{
			"fieldname":"holiday_list",
			"label": __("Holiday List"),
			"fieldtype": "Link",
			"options": "Holiday List"
		}
	]
}
