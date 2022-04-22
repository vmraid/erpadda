// Copyright (c) 2016, VMRaid and contributors
// For license information, please see license.txt
/* eslint-disable */

{% include "erpadda/regional/report/india_gst_common/india_gst_common.js" %}

vmraid.query_reports["HSN-wise-summary of outward supplies"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"reqd": 1,
			"default": vmraid.defaults.get_user_default("Company"),
			"on_change": fetch_gstins
		},
		{
			"fieldname":"gst_hsn_code",
			"label": __("HSN/SAC"),
			"fieldtype": "Link",
			"options": "GST HSN Code",
			"width": "80"
		},
		{
			"fieldname":"company_gstin",
			"label": __("Company GSTIN"),
			"fieldtype": "Select",
			"placeholder":"Company GSTIN",
			"options": [""],
			"width": "80"
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80"
		},

	],
	onload: (report) => {
		fetch_gstins(report);

		report.page.add_inner_button(__("Download JSON"), function () {
			var filters = report.get_values();

			vmraid.call({
				method: 'erpadda.regional.report.hsn_wise_summary_of_outward_supplies.hsn_wise_summary_of_outward_supplies.get_json',
				args: {
					data: report.data,
					report_name: report.report_name,
					filters: filters
				},
				callback: function(r) {
					if (r.message) {
						const args = {
							cmd: 'erpadda.regional.report.hsn_wise_summary_of_outward_supplies.hsn_wise_summary_of_outward_supplies.download_json_file',
							data: r.message.data,
							report_name: r.message.report_name
						};
						open_url_post(vmraid.request.url, args);
					}
				}
			});
		});
	}
};
