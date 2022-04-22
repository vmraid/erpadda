// Copyright (c) 2015, VMRaid and Contributors
// License: GNU General Public License v3. See license.txt

vmraid.require("assets/erpadda/js/financial_statements.js", function() {
	vmraid.query_reports["Balance Sheet"] = $.extend({}, erpadda.financial_statements);

	erpadda.utils.add_dimensions('Balance Sheet', 10);

	vmraid.query_reports["Balance Sheet"]["filters"].push({
		"fieldname": "accumulated_values",
		"label": __("Accumulated Values"),
		"fieldtype": "Check",
		"default": 1
	});

	vmraid.query_reports["Balance Sheet"]["filters"].push({
		"fieldname": "include_default_book_entries",
		"label": __("Include Default Book Entries"),
		"fieldtype": "Check",
		"default": 1
	});
});
