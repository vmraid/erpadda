// Copyright (c) 2015, VMRaid and Contributors
// License: GNU General Public License v3. See license.txt

vmraid.provide("erpadda.maintenance");
vmraid.ui.form.on('Maintenance Visit', {
	setup: function (frm) {
		frm.set_query('contact_person', erpadda.queries.contact_query);
		frm.set_query('customer_address', erpadda.queries.address_query);
		frm.set_query('customer', erpadda.queries.customer);
	},
	onload: function (frm) {
		// filters for serial no based on item code
		if (frm.doc.maintenance_type === "Scheduled") {
			let item_code = frm.doc.purposes[0].item_code;
			if (!item_code) {
				return;
			}
			vmraid.call({
				method: "erpadda.maintenance.doctype.maintenance_schedule.maintenance_schedule.get_serial_nos_from_schedule",
				args: {
					schedule: frm.doc.maintenance_schedule,
					item_code: item_code
				}
			}).then((r) => {
				let serial_nos = r.message;
				frm.set_query('serial_no', 'purposes', () => {
					if (serial_nos.length > 0) {
						return {
							filters: {
								'item_code': item_code,
								'name': ["in", serial_nos]
							}
						};
					}
					return {
						filters: {
							'item_code': item_code
						}
					};
				});
			});
		} else {
			frm.set_query('serial_no', 'purposes', (frm, cdt, cdn) => {
				let row = locals[cdt][cdn];
				return {
					filters: {
						'item_code': row.item_code
					}
				};
			});
		}
		if (!frm.doc.status) {
			frm.set_value({ status: 'Draft' });
		}
		if (frm.doc.__islocal) {
			frm.set_value({ mntc_date: vmraid.datetime.get_today() });
		}
	},
	customer: function (frm) {
		erpadda.utils.get_party_details(frm);
	},
	customer_address: function (frm) {
		erpadda.utils.get_address_display(frm, 'customer_address', 'address_display');
	},
	contact_person: function (frm) {
		erpadda.utils.get_contact_details(frm);
	}
})

// TODO commonify this code
erpadda.maintenance.MaintenanceVisit = class MaintenanceVisit extends vmraid.ui.form.Controller {
	refresh() {
		vmraid.dynamic_link = {doc: this.frm.doc, fieldname: 'customer', doctype: 'Customer'}

		var me = this;

		if (this.frm.doc.docstatus === 0) {
			this.frm.add_custom_button(__('Maintenance Schedule'),
				function () {
					if (!me.frm.doc.customer) {
						vmraid.msgprint(__('Please select Customer first'));
						return;
					}
					erpadda.utils.map_current_doc({
						method: "erpadda.maintenance.doctype.maintenance_schedule.maintenance_schedule.make_maintenance_visit",
						source_doctype: "Maintenance Schedule",
						target: me.frm,
						setters: {
							customer: me.frm.doc.customer,
						},
						get_query_filters: {
							docstatus: 1,
							company: me.frm.doc.company
						}
					})
				}, __("Get Items From"));
			this.frm.add_custom_button(__('Warranty Claim'),
				function () {
					erpadda.utils.map_current_doc({
						method: "erpadda.support.doctype.warranty_claim.warranty_claim.make_maintenance_visit",
						source_doctype: "Warranty Claim",
						target: me.frm,
						date_field: "complaint_date",
						setters: {
							customer: me.frm.doc.customer || undefined,
						},
						get_query_filters: {
							status: ["in", "Open, Work in Progress"],
							company: me.frm.doc.company
						}
					})
				}, __("Get Items From"));
			this.frm.add_custom_button(__('Sales Order'),
				function () {
					if (!me.frm.doc.customer) {
						vmraid.msgprint(__('Please select Customer first'));
						return;
					}
					erpadda.utils.map_current_doc({
						method: "erpadda.selling.doctype.sales_order.sales_order.make_maintenance_visit",
						source_doctype: "Sales Order",
						target: me.frm,
						setters: {
							customer: me.frm.doc.customer,
						},
						get_query_filters: {
							docstatus: 1,
							company: me.frm.doc.company,
							order_type: me.frm.doc.order_type,
						}
					})
				}, __("Get Items From"));
		}
	}
};

extend_cscript(cur_frm.cscript, new erpadda.maintenance.MaintenanceVisit({frm: cur_frm}));
