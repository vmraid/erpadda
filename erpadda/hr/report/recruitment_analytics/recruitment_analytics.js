// Copyright (c) 2016, VMRaid and contributors
// For license information, please see license.txt
/* eslint-disable */

vmraid.query_reports["Recruitment Analytics"] = {
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
			"fieldname":"on_date",
			"label": __("On Date"),
			"fieldtype": "Date",
			"default": vmraid.datetime.now_date(),
			"reqd": 1,
		},
	]
};
