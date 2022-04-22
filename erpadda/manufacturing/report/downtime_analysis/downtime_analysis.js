// Copyright (c) 2016, VMRaid and contributors
// For license information, please see license.txt
/* eslint-disable */

vmraid.query_reports["Downtime Analysis"] = {
	"filters": [
		{
			label: __("From Date"),
			fieldname:"from_date",
			fieldtype: "Datetime",
			default: vmraid.datetime.convert_to_system_tz(vmraid.datetime.add_months(vmraid.datetime.now_datetime(), -1)),
			reqd: 1
		},
		{
			label: __("To Date"),
			fieldname:"to_date",
			fieldtype: "Datetime",
			default: vmraid.datetime.now_datetime(),
			reqd: 1,
		},
		{
			label: __("Machine"),
			fieldname: "workstation",
			fieldtype: "Link",
			options: "Workstation"
		}
	]
};
