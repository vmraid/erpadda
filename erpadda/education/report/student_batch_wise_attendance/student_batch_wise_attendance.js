// Copyright (c) 2016, VMRaid and contributors
// For license information, please see license.txt

vmraid.query_reports["Student Batch-Wise Attendance"] = {
	"filters": [{
		"fieldname": "date",
		"label": __("Date"),
		"fieldtype": "Date",
		"default": vmraid.datetime.get_today(),
		"reqd": 1
	}]
}
