// Copyright (c) 2016, VMRaid and contributors
// For license information, please see license.txt
/* eslint-disable */

vmraid.query_reports["Employee Analytics"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": vmraid.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname":"parameter",
			"label": __("Parameter"),
			"fieldtype": "Select",
			"options": ["Branch","Grade","Department","Designation", "Employment Type"],
			"reqd": 1
		}
	]
};
