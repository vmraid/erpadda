// Copyright (c) 2016, VMRaid and contributors
// For license information, please see license.txt
/* eslint-disable */

vmraid.query_reports["Loan Repayment and Closure"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"reqd": 1,
			"default": vmraid.defaults.get_user_default("Company")
		},
		{
			"fieldname":"applicant_type",
			"label": __("Applicant Type"),
			"fieldtype": "Select",
			"options": ["Customer", "Employee"],
			"reqd": 1,
			"default": "Customer",
			on_change: function() {
				vmraid.query_report.set_filter_value('applicant', "");
			}
		},
		{
			"fieldname": "applicant",
			"label": __("Applicant"),
			"fieldtype": "Dynamic Link",
			"get_options": function() {
				var applicant_type = vmraid.query_report.get_filter_value('applicant_type');
				var applicant = vmraid.query_report.get_filter_value('applicant');
				if(applicant && !applicant_type) {
					vmraid.throw(__("Please select Applicant Type first"));
				}
				return applicant_type;
			}

		},
	]
};
