// Copyright (c) 2016, VMRaid and contributors
// For license information, please see license.txt

vmraid.query_reports["Item Prices"] = {
	"filters": [
		{
			"fieldname": "items",
			"label": __("Items Filter"),
			"fieldtype": "Select",
			"options": "Enabled Items only\nDisabled Items only\nAll Items",
			"default": "Enabled Items only",
			"on_change": function(query_report) {
				query_report.trigger_refresh();
			}
		}
	]
}
