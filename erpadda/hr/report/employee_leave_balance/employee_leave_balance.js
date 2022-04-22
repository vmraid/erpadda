// Copyright (c) 2015, VMRaid and Contributors
// License: GNU General Public License v3. See license.txt

vmraid.query_reports["Employee Leave Balance"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": vmraid.defaults.get_default("year_start_date")
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": vmraid.defaults.get_default("year_end_date")
		},
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"reqd": 1,
			"default": vmraid.defaults.get_user_default("Company")
		},
		{
			"fieldname":"department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options": "Department",
		},
		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
		}
	],

	onload: () => {
		vmraid.call({
			type: "GET",
			method: "erpadda.hr.utils.get_leave_period",
			args: {
				"from_date": vmraid.defaults.get_default("year_start_date"),
				"to_date": vmraid.defaults.get_default("year_end_date"),
				"company": vmraid.defaults.get_user_default("Company")
			},
			freeze: true,
			callback: (data) => {
				vmraid.query_report.set_filter_value("from_date", data.message[0].from_date);
				vmraid.query_report.set_filter_value("to_date", data.message[0].to_date);
			}
		});
	}
}
