// Copyright (c) 2016, VMRaid and contributors
// For license information, please see license.txt
/* eslint-disable */

vmraid.query_reports["Employee Exits"] = {
	filters: [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": vmraid.datetime.add_months(vmraid.datetime.nowdate(), -12)
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": vmraid.datetime.nowdate()
		},
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company"
		},
		{
			"fieldname": "department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options": "Department"
		},
		{
			"fieldname": "designation",
			"label": __("Designation"),
			"fieldtype": "Link",
			"options": "Designation"
		},
		{
			"fieldname": "employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee"
		},
		{
			"fieldname": "reports_to",
			"label": __("Reports To"),
			"fieldtype": "Link",
			"options": "Employee"
		},
		{
			"fieldname": "interview_status",
			"label": __("Interview Status"),
			"fieldtype": "Select",
			"options": ["", "Pending", "Scheduled", "Completed"]
		},
		{
			"fieldname": "final_decision",
			"label": __("Final Decision"),
			"fieldtype": "Select",
			"options": ["", "Employee Retained", "Exit Confirmed"]
		},
		{
			"fieldname": "exit_interview_pending",
			"label": __("Exit Interview Pending"),
			"fieldtype": "Check"
		},
		{
			"fieldname": "questionnaire_pending",
			"label": __("Exit Questionnaire Pending"),
			"fieldtype": "Check"
		},
		{
			"fieldname": "fnf_pending",
			"label": __("FnF Pending"),
			"fieldtype": "Check"
		}
	]
};
