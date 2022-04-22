// Copyright (c) 2015, VMRaid and Contributors and contributors
// For license information, please see license.txt

vmraid.query_reports["Customer Credit Balance"] = {
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
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer"
		}
	]
}
