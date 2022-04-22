// Copyright (c) 2016, VMRaid and contributors
// For license information, please see license.txt
/* eslint-disable */

vmraid.query_reports["First Response Time for Opportunity"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": vmraid.datetime.add_days(vmraid.datetime.nowdate(), -30)
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": vmraid.datetime.nowdate()
		},
	],
	get_chart_data: function (_columns, result) {
		return {
			data: {
				labels: result.map(d => d.creation_date),
				datasets: [{
					name: "First Response Time",
					values: result.map(d => d.first_response_time)
				}]
			},
			type: "line",
			tooltipOptions: {
				formatTooltipY: d => {
					let duration_options = {
						hide_days: 0,
						hide_seconds: 0
					};
					return vmraid.utils.get_formatted_duration(d, duration_options);
				}
			}
		}
	}
};
