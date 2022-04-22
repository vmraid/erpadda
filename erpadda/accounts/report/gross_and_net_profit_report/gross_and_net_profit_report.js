// Copyright (c) 2016, VMRaid and contributors
// For license information, please see license.txt
/* eslint-disable */

vmraid.query_reports["Gross and Net Profit Report"] = {
	"filters": [

	]
}
vmraid.require("assets/erpadda/js/financial_statements.js", function() {
	vmraid.query_reports["Gross and Net Profit Report"] = $.extend({},
		erpadda.financial_statements);

	vmraid.query_reports["Gross and Net Profit Report"]["filters"].push(
		{
			"fieldname": "project",
			"label": __("Project"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return vmraid.db.get_link_options('Project', txt);
			}
		},
		{
			"fieldname": "accumulated_values",
			"label": __("Accumulated Values"),
			"fieldtype": "Check"
		}
	);
});
