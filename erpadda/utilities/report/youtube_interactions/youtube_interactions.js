// Copyright (c) 2016, VMRaid and contributors
// For license information, please see license.txt
/* eslint-disable */

vmraid.query_reports["YouTube Interactions"] = {
	"filters": [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: vmraid.datetime.add_months(vmraid.datetime.now_date(), -12),
		},
		{
			fieldname:"to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: vmraid.datetime.now_date(),
		}
	]
};
