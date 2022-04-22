// Copyright (c) 2015, VMRaid and Contributors
// License: GNU General Public License v3. See license.txt

vmraid.require("assets/erpadda/js/sales_trends_filters.js", function() {
	vmraid.query_reports["Delivery Note Trends"] = {
		filters: erpadda.get_sales_trends_filters()
	}
});
