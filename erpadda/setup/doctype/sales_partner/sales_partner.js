// Copyright (c) 2015, VMRaid and Contributors
// License: GNU General Public License v3. See license.txt

vmraid.ui.form.on('Sales Partner', {
	refresh: function(frm) {
		vmraid.dynamic_link = {doc: frm.doc, fieldname: 'name', doctype: 'Sales Partner'}

		if(frm.doc.__islocal){
			hide_field(['address_html', 'contact_html', 'address_contacts']);
			vmraid.contacts.clear_address_and_contact(frm);
		}
		else{
			unhide_field(['address_html', 'contact_html', 'address_contacts']);
			vmraid.contacts.render_address_and_contact(frm);
		}
	},

	setup: function(frm) {
		frm.fields_dict["targets"].grid.get_field("distribution_id").get_query = function(doc, cdt, cdn){
			var row = locals[cdt][cdn];
			return {
				filters: {
					'fiscal_year': row.fiscal_year
				}
			}
		};
	},
	referral_code:function(frm){
		if (frm.doc.referral_code) {
			frm.doc.referral_code=frm.doc.referral_code.toUpperCase();
			frm.refresh_field('referral_code');
		}
	}
});
