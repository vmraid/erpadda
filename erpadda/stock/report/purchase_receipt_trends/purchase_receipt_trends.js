// Copyright (c) 2015, VMRaid and Contributors
// License: GNU General Public License v3. See license.txt

vmraid.require("assets/erpadda/js/purchase_trends_filters.js", function() {
	vmraid.query_reports["Purchase Receipt Trends"] = {
		filters: erpadda.get_purchase_trends_filters()
	}
});
