// Copyright (c) 2016, VMRaid and contributors
// For license information, please see license.txt
/* eslint-disable */

vmraid.query_reports["Quality Inspection Summary"] = {
	"filters": [
		{
			label: __("From Date"),
			fieldname:"from_date",
			fieldtype: "Date",
			default: vmraid.datetime.add_months(vmraid.datetime.get_today(), -12),
			reqd: 1
		},
		{
			label: __("To Date"),
			fieldname:"to_date",
			fieldtype: "Date",
			default: vmraid.datetime.get_today(),
			reqd: 1,
		},
		{
			label: __("Status"),
			fieldname: "status",
			fieldtype: "Select",
			options: ["", "Accepted", "Rejected"]
		},
		{
			label: __("Item Code"),
			fieldname: "item_code",
			fieldtype: "Link",
			options: "Item"
		},
		{
			label: __("Inspected By"),
			fieldname: "inspected_by",
			fieldtype: "Link",
			options: "User"
		}
	]
};
