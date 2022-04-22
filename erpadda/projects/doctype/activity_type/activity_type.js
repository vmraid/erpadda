vmraid.ui.form.on("Activity Type", {
	onload: function(frm) {
		frm.set_currency_labels(["billing_rate", "costing_rate"], vmraid.defaults.get_global_default('currency'));
	},

	refresh: function(frm) {
		frm.add_custom_button(__("Activity Cost per Employee"), function() {
			vmraid.route_options = {"activity_type": frm.doc.name};
			vmraid.set_route("List", "Activity Cost");
		});
	}
});
