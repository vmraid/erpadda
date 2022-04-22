// Copyright (c) 2016, VMRaid and contributors
// For license information, please see license.txt
/* eslint-disable */

vmraid.query_reports["Final Assessment Grades"] = {
	"filters": [
		{
			"fieldname":"academic_year",
			"label": __("Academic Year"),
			"fieldtype": "Link",
			"options": "Academic Year",
			"reqd": 1
		},
		{
			"fieldname":"student_group",
			"label": __("Student Group"),
			"fieldtype": "Link",
			"options": "Student Group",
			"reqd": 1,
			"get_query": function() {
				return{
					filters: {
						"group_based_on": "Batch",
						"academic_year": vmraid.query_report.get_filter_value('academic_year')
					}
				};
			}
		},
		{
			"fieldname":"assessment_group",
			"label": __("Assessment Group"),
			"fieldtype": "Link",
			"options": "Assessment Group",
			"reqd": 1
		}

	]
}
