// Copyright (c) 2015, VMRaid and Contributors
// License: GNU General Public License v3. See license.txt

// render
vmraid.listview_settings['POS Closing Entry'] = {
	get_indicator: function(doc) {
		var status_color = {
			"Draft": "red",
			"Submitted": "blue",
			"Queued": "orange",
			"Failed": "red",
			"Cancelled": "red"

		};
		return [__(doc.status), status_color[doc.status], "status,=,"+doc.status];
	}
};
