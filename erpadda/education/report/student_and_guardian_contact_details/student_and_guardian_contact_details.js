// Copyright (c) 2016, VMRaid and contributors
// For license information, please see license.txt

vmraid.query_reports["Student and Guardian Contact Details"] = {
	"filters": [
		{
			"fieldname":"academic_year",
			"label": __("Academic Year"),
			"fieldtype": "Link",
			"options": "Academic Year",
			"reqd": 1,
		},
		{
			"fieldname":"program",
			"label": __("Program"),
			"fieldtype": "Link",
			"options": "Program",
			"reqd": 1
		},
		{
			"fieldname":"student_batch_name",
			"label": __("Batch Name"),
			"fieldtype": "Link",
			"options": "Student Batch Name",
			"reqd": 1
		},

	]
}
