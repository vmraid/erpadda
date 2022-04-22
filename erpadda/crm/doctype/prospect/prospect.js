// Copyright (c) 2021, VMRaid and contributors
// For license information, please see license.txt

vmraid.ui.form.on('Prospect', {
	refresh (frm) {
		vmraid.dynamic_link = { doc: frm.doc, fieldname: "name", doctype: frm.doctype };

		if (!frm.is_new() && vmraid.boot.user.can_create.includes("Customer")) {
			frm.add_custom_button(__("Customer"), function() {
				vmraid.model.open_mapped_doc({
					method: "erpadda.crm.doctype.prospect.prospect.make_customer",
					frm: frm
				});
			}, __("Create"));
		}
		if (!frm.is_new() && vmraid.boot.user.can_create.includes("Opportunity")) {
			frm.add_custom_button(__("Opportunity"), function() {
				vmraid.model.open_mapped_doc({
					method: "erpadda.crm.doctype.prospect.prospect.make_opportunity",
					frm: frm
				});
			}, __("Create"));
		}

		if (!frm.is_new()) {
			vmraid.contacts.render_address_and_contact(frm);
		} else {
			vmraid.contacts.clear_address_and_contact(frm);
		}
	}
});
