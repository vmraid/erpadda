// Copyright (c) 2017, VMRaid and contributors
// For license information, please see license.txt

vmraid.ui.form.on('Manufacturer', {
	refresh: function(frm) {
		vmraid.dynamic_link = { doc: frm.doc, fieldname: 'name', doctype: 'Manufacturer' };
		if (frm.doc.__islocal) {
			hide_field(['address_html','contact_html']);
			vmraid.contacts.clear_address_and_contact(frm);
		}
		else {
			unhide_field(['address_html','contact_html']);
			vmraid.contacts.render_address_and_contact(frm);
		}
	}
});
