// Copyright (c) 2016, VMRaid and contributors
// For license information, please see license.txt
vmraid.query_reports["Vehicle Expenses"] = {
	"filters": [
		{
			"fieldname": "filter_based_on",
			"label": __("Filter Based On"),
			"fieldtype": "Select",
			"options": ["Fiscal Year", "Date Range"],
			"default": ["Fiscal Year"],
			"reqd": 1
		},
		{
			"fieldname": "fiscal_year",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"default": vmraid.defaults.get_user_default("fiscal_year"),
			"depends_on": "eval: doc.filter_based_on == 'Fiscal Year'",
			"reqd": 1
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"depends_on": "eval: doc.filter_based_on == 'Date Range'",
			"default": vmraid.datetime.add_months(vmraid.datetime.nowdate(), -12)
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"depends_on": "eval: doc.filter_based_on == 'Date Range'",
			"default": vmraid.datetime.nowdate()
		},
		{
			"fieldname": "vehicle",
			"label": __("Vehicle"),
			"fieldtype": "Link",
			"options": "Vehicle"
		},
		{
			"fieldname": "employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee"
		}
	]
};
