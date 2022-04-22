// Copyright (c) 2019, VMRaid and Contributors
// License: GNU General Public License v3. See license.txt

// render
vmraid.listview_settings['Leave Allocation'] = {
	get_indicator: function(doc) {
		if(doc.status==="Expired") {
			return [__("Expired"), "gray", "expired, =, 1"];
		}
	},
};
