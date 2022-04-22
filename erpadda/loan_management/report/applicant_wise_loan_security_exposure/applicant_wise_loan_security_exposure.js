// Copyright (c) 2016, VMRaid and contributors
// For license information, please see license.txt
/* eslint-disable */

vmraid.query_reports["Applicant-Wise Loan Security Exposure"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": vmraid.defaults.get_user_default("Company"),
			"reqd": 1
		}
	]
};
