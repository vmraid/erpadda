// Copyright (c) 2015, VMRaid and Contributors
// License: GNU General Public License v3. See license.txt


vmraid.require("assets/erpadda/js/financial_statements.js", function() {
	vmraid.query_reports["Profit and Loss Statement"] = $.extend({},
		erpadda.financial_statements);

	erpadda.utils.add_dimensions('Profit and Loss Statement', 10);

	vmraid.query_reports["Profit and Loss Statement"]["filters"].push(
		{
			"fieldname": "project",
			"label": __("Project"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return vmraid.db.get_link_options('Project', txt);
			}
		},
		{
			"fieldname": "include_default_book_entries",
			"label": __("Include Default Book Entries"),
			"fieldtype": "Check",
			"default": 1
		}
	);
});
