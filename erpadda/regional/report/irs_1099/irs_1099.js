// Copyright (c) 2018, VMRaid and Contributors
// License: GNU General Public License v3. See license.txt

vmraid.query_reports["IRS 1099"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": vmraid.defaults.get_user_default("Company"),
			"reqd": 1,
			"width": 80,
		},
		{
			"fieldname": "fiscal_year",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"default": vmraid.defaults.get_user_default("fiscal_year"),
			"reqd": 1,
			"width": 80,
		},
		{
			"fieldname": "supplier_group",
			"label": __("Supplier Group"),
			"fieldtype": "Link",
			"options": "Supplier Group",
			"default": "",
			"reqd": 0,
			"width": 80
		},
	],

	onload: function (query_report) {
		query_report.page.add_inner_button(__("Print IRS 1099 Forms"), () => {
			build_1099_print(query_report);
		});
	}
};

function build_1099_print(query_report) {
	let filters = JSON.stringify(query_report.get_values());
	let w = window.open('/api/method/erpadda.regional.report.irs_1099.irs_1099.irs_1099_print?' +
		'&filters=' + encodeURIComponent(filters));
	// w.print();
}
