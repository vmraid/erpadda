// Copyright (c) 2021, VMRaid and contributors
// For license information, please see license.txt

vmraid.ui.form.on('Campaign', {
	refresh: function(frm) {
		erpadda.toggle_naming_series();

		if (frm.is_new()) {
			frm.toggle_display("naming_series", vmraid.boot.sysdefaults.campaign_naming_by=="Naming Series");
		} else {
			cur_frm.add_custom_button(__("View Leads"), function() {
				vmraid.route_options = {"source": "Campaign", "campaign_name": frm.doc.name};
				vmraid.set_route("List", "Lead");
			}, "fa fa-list", true);
		}
	}
});
