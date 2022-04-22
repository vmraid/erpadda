// Copyright (c) 2016, VMRaid and contributors
// For license information, please see license.txt
/* eslint-disable */

vmraid.require("assets/erpadda/js/salary_slip_deductions_report_filters.js", function() {

	let ecs_checklist_filter = erpadda.salary_slip_deductions_report_filters
	ecs_checklist_filter['filters'].push({
		fieldname: "type",
		label: __("Type"),
		fieldtype: "Select",
		options:["", "Bank", "Cash", "Cheque"]
	})

	vmraid.query_reports["Salary Payments via ECS"] = ecs_checklist_filter
});
