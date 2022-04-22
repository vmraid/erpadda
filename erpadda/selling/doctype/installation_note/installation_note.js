// Copyright (c) 2015, VMRaid and Contributors
// License: GNU General Public License v3. See license.txt

vmraid.ui.form.on('Installation Note', {
	setup: function(frm) {
		vmraid.dynamic_link = {doc: frm.doc, fieldname: 'customer', doctype: 'Customer'}
		frm.set_query('customer_address', erpadda.queries.address_query);
		frm.set_query('contact_person', erpadda.queries.contact_query);
		frm.set_query('customer', erpadda.queries.customer);
	},
	onload: function(frm) {
		if(!frm.doc.status) {
			frm.set_value({ status:'Draft'});
		}
		if(frm.doc.__islocal) {
			frm.set_value({inst_date: vmraid.datetime.get_today()});
		}
	},
	customer: function(frm) {
		erpadda.utils.get_party_details(frm);
	},
	customer_address: function(frm) {
		erpadda.utils.get_address_display(frm);
	},
	contact_person: function(frm) {
		erpadda.utils.get_contact_details(frm);
	}
});

vmraid.provide("erpadda.selling");

// TODO commonify this code
erpadda.selling.InstallationNote = class InstallationNote extends vmraid.ui.form.Controller {
	refresh() {
		var me = this;
		if (this.frm.doc.docstatus===0) {
			this.frm.add_custom_button(__('From Delivery Note'),
				function() {
					erpadda.utils.map_current_doc({
						method: "erpadda.stock.doctype.delivery_note.delivery_note.make_installation_note",
						source_doctype: "Delivery Note",
						target: me.frm,
						date_field: "posting_date",
						setters: {
							customer: me.frm.doc.customer || undefined,
						},
						get_query_filters: {
							docstatus: 1,
							status: ["not in", ["Stopped", "Closed"]],
							per_installed: ["<", 99.99],
							company: me.frm.doc.company
						}
					})
				}, "fa fa-download", "btn-default"
			);
		}
	}
};

extend_cscript(cur_frm.cscript, new erpadda.selling.InstallationNote({frm: cur_frm}));
