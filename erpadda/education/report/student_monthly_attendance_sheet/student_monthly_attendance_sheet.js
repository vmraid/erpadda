// Copyright (c) 2015, VMRaid and Contributors
// License: GNU General Public License v3. See license.txt


vmraid.query_reports["Student Monthly Attendance Sheet"] = {
	"filters": [{
		"fieldname": "month",
		"label": __("Month"),
		"fieldtype": "Select",
		"options": "Jan\nFeb\nMar\nApr\nMay\nJun\nJul\nAug\nSep\nOct\nNov\nDec",
		"default": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
			"Dec"
		][vmraid.datetime.str_to_obj(vmraid.datetime.get_today()).getMonth()],
	},
	{
		"fieldname": "year",
		"label": __("Year"),
		"fieldtype": "Select",
		"reqd": 1
	},
	{
		"fieldname": "student_group",
		"label": __("Student Group"),
		"fieldtype": "Link",
		"options": "Student Group",
		"reqd": 1
	}
	],

	"onload": function() {
		return vmraid.call({
			method: "erpadda.education.report.student_monthly_attendance_sheet.student_monthly_attendance_sheet.get_attendance_years",
			callback: function(r) {
				var year_filter = vmraid.query_report.get_filter('year');
				year_filter.df.options = r.message;
				year_filter.df.default = r.message.split("\n")[0];
				year_filter.refresh();
				year_filter.set_input(year_filter.df.default);
			}
		});
	}
}
