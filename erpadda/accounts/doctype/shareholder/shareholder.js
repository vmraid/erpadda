// Copyright (c) 2017, VMRaid and contributors
// For license information, please see license.txt

vmraid.ui.form.on('Shareholder', {
	refresh: function(frm) {
		vmraid.dynamic_link = { doc: frm.doc, fieldname: 'name', doctype: 'Shareholder' };

		frm.toggle_display(['contact_html'], !frm.doc.__islocal);

		if (frm.doc.__islocal) {
			hide_field(['contact_html']);
			vmraid.contacts.clear_address_and_contact(frm);
		}
		else {
			if (frm.doc.is_company){
				hide_field(['company']);
			} else {
				unhide_field(['contact_html']);
				vmraid.contacts.render_address_and_contact(frm);
			}
		}

		if (frm.doc.folio_no != undefined){
			frm.add_custom_button(__("Share Balance"), function(){
				vmraid.route_options = {
					"shareholder": frm.doc.name,
				};
				vmraid.set_route("query-report", "Share Balance");
			});
			frm.add_custom_button(__("Share Ledger"), function(){
				vmraid.route_options = {
					"shareholder": frm.doc.name,
				};
				vmraid.set_route("query-report", "Share Ledger");
			});
			let fields = ['title', 'folio_no', 'company'];
			fields.forEach((fieldname) => {
				frm.fields_dict[fieldname].df.read_only = 1;
				frm.refresh_fields(fieldname);
			});
			$(`.btn:contains("New Contact"):visible`).hide();
			$(`.btn:contains("Edit"):visible`).hide();
		}
	},
	validate: (frm) => {
		let contact_list = {
			contacts: []
		};
		$('div[data-fieldname=contact_html] > .address-box').each( (index, ele) => {
			contact_list.contacts.push(ele.innerText.replace(' Edit', ''));
		});
		frm.doc.contact_list = JSON.stringify(contact_list);
	}
});
