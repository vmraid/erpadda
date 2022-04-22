// Copyright (c) 2018, VMRaid and Contributors
// MIT License. See license.txt
vmraid.provide("vmraid.desk");

vmraid.ui.form.on("Event", {
	refresh: function(frm) {
		frm.set_query('reference_doctype', "event_participants", function() {
			return {
				"filters": {
					"name": ["in", ["Contact", "Lead", "Customer", "Supplier", "Employee", "Sales Partner"]]
				}
			};
		});

		frm.add_custom_button(__('Add Leads'), function() {
			new vmraid.desk.eventParticipants(frm, "Lead");
		}, __("Add Participants"));

		frm.add_custom_button(__('Add Customers'), function() {
			new vmraid.desk.eventParticipants(frm, "Customer");
		}, __("Add Participants"));

		frm.add_custom_button(__('Add Suppliers'), function() {
			new vmraid.desk.eventParticipants(frm, "Supplier");
		}, __("Add Participants"));

		frm.add_custom_button(__('Add Employees'), function() {
			new vmraid.desk.eventParticipants(frm, "Employee");
		}, __("Add Participants"));

		frm.add_custom_button(__('Add Sales Partners'), function() {
			new vmraid.desk.eventParticipants(frm, "Sales Partners");
		}, __("Add Participants"));
	}
});
