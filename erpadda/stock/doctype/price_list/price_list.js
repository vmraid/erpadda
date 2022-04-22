// Copyright (c) 2015, VMRaid and Contributors
// License: GNU General Public License v3. See license.txt

vmraid.ui.form.on("Price List", {
	refresh: function(frm) {
		let me = this;
		frm.add_custom_button(__("Add / Edit Prices"), function() {
			vmraid.route_options = {
				"price_list": frm.doc.name
			};
			vmraid.set_route("Report", "Item Price");
		}, "fa fa-money");
	}
});
