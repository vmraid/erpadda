// Copyright (c) 2015, VMRaid and Contributors
// License: GNU General Public License v3. See license.txt

// render
vmraid.listview_settings['Loan Security Unpledge'] = {
	add_fields: ["status"],
	get_indicator: function(doc) {
		var status_color = {
			"Requested": "orange",
			"Approved": "green",
		};
		return [__(doc.status), status_color[doc.status], "status,=,"+doc.status];
	}
};
