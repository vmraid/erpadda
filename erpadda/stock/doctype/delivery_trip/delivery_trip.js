// Copyright (c) 2017, VMRaid and contributors
// For license information, please see license.txt

vmraid.ui.form.on('Delivery Trip', {
	setup: function (frm) {
		frm.set_indicator_formatter('customer', (stop) => (stop.visited) ? "green" : "orange");

		frm.set_query("driver", function () {
			return {
				filters: {
					"status": "Active"
				}
			};
		});

		frm.set_query("address", "delivery_stops", function (doc, cdt, cdn) {
			var row = locals[cdt][cdn];
			if (row.customer) {
				return {
					query: 'vmraid.contacts.doctype.address.address.address_query',
					filters: {
						link_doctype: "Customer",
						link_name: row.customer
					}
				};
			}
		})

		frm.set_query("contact", "delivery_stops", function (doc, cdt, cdn) {
			var row = locals[cdt][cdn];
			if (row.customer) {
				return {
					query: 'vmraid.contacts.doctype.contact.contact.contact_query',
					filters: {
						link_doctype: "Customer",
						link_name: row.customer
					}
				};
			}
		})
	},

	refresh: function (frm) {
		if (frm.doc.docstatus == 1 && frm.doc.employee) {
			frm.add_custom_button(__('Expense Claim'), function() {
				vmraid.model.open_mapped_doc({
					method: 'erpadda.stock.doctype.delivery_trip.delivery_trip.make_expense_claim',
					frm: cur_frm,
				});
			}, __("Create"));
		}

		if (frm.doc.docstatus == 1 && frm.doc.delivery_stops.length > 0) {
			frm.add_custom_button(__("Notify Customers via Email"), function () {
				frm.trigger('notify_customers');
			});
		}

		if (frm.doc.docstatus === 0) {
			frm.add_custom_button(__('Delivery Note'), () => {
				erpadda.utils.map_current_doc({
					method: "erpadda.stock.doctype.delivery_note.delivery_note.make_delivery_trip",
					source_doctype: "Delivery Note",
					target: frm,
					date_field: "posting_date",
					setters: {
						company: frm.doc.company,
					},
					get_query_filters: {
						docstatus: 1,
						company: frm.doc.company,
					}
				})
			}, __("Get customers from"));
		}
	},

	calculate_arrival_time: function (frm) {
		if (!frm.doc.driver_address) {
			vmraid.throw(__("Cannot Calculate Arrival Time as Driver Address is Missing."));
		}
		vmraid.show_alert({
			message: "Calculating Arrival Times",
			indicator: 'orange'
		});
		frm.call("process_route", {
			optimize: false,
		}, () => {
			frm.reload_doc();
		});
	},

	driver: function (frm) {
		if (frm.doc.driver) {
			vmraid.call({
				method: "erpadda.stock.doctype.delivery_trip.delivery_trip.get_driver_email",
				args: {
					driver: frm.doc.driver
				},
				callback: (data) => {
					frm.set_value("driver_email", data.message.email);
				}
			});
		};
	},

	optimize_route: function (frm) {
		if (!frm.doc.driver_address) {
			vmraid.throw(__("Cannot Optimize Route as Driver Address is Missing."));
		}
		vmraid.show_alert({
			message: "Optimizing Route",
			indicator: 'orange'
		});
		frm.call("process_route", {
			optimize: true,
		}, () => {
			frm.reload_doc();
		});
	},

	notify_customers: function (frm) {
		$.each(frm.doc.delivery_stops || [], function (i, delivery_stop) {
			if (!delivery_stop.delivery_note) {
				vmraid.msgprint({
					"message": __("No Delivery Note selected for Customer {}", [delivery_stop.customer]),
					"title": __("Warning"),
					"indicator": "orange",
					"alert": 1
				});
			}
		});

		vmraid.db.get_value("Delivery Settings", { name: "Delivery Settings" }, "dispatch_template", (r) => {
			if (!r.dispatch_template) {
				vmraid.throw(__("Missing email template for dispatch. Please set one in Delivery Settings."));
			} else {
				vmraid.confirm(__("Do you want to notify all the customers by email?"), function () {
					vmraid.call({
						method: "erpadda.stock.doctype.delivery_trip.delivery_trip.notify_customers",
						args: {
							"delivery_trip": frm.doc.name
						},
						callback: function (r) {
							if (!r.exc) {
								frm.doc.email_notification_sent = true;
								frm.refresh_field('email_notification_sent');
							}
						}
					});
				});
			}
		});
	}
});

vmraid.ui.form.on('Delivery Stop', {
	customer: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		if (row.customer) {
			vmraid.call({
				method: "erpadda.stock.doctype.delivery_trip.delivery_trip.get_contact_and_address",
				args: { "name": row.customer },
				callback: function (r) {
					if (r.message) {
						if (r.message["shipping_address"]) {
							vmraid.model.set_value(cdt, cdn, "address", r.message["shipping_address"].parent);
						}
						else {
							vmraid.model.set_value(cdt, cdn, "address", '');
						}
						if (r.message["contact_person"]) {
							vmraid.model.set_value(cdt, cdn, "contact", r.message["contact_person"].parent);
						}
						else {
							vmraid.model.set_value(cdt, cdn, "contact", '');
						}
					}
					else {
						vmraid.model.set_value(cdt, cdn, "address", '');
						vmraid.model.set_value(cdt, cdn, "contact", '');
					}
				}
			});
		}
	},

	address: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		if (row.address) {
			vmraid.call({
				method: "vmraid.contacts.doctype.address.address.get_address_display",
				args: { "address_dict": row.address },
				callback: function (r) {
					if (r.message) {
						vmraid.model.set_value(cdt, cdn, "customer_address", r.message);
					}
				}
			});
		} else {
			vmraid.model.set_value(cdt, cdn, "customer_address", "");
		}
	},

	contact: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		if (row.contact) {
			vmraid.call({
				method: "erpadda.stock.doctype.delivery_trip.delivery_trip.get_contact_display",
				args: { "contact": row.contact },
				callback: function (r) {
					if (r.message) {
						vmraid.model.set_value(cdt, cdn, "customer_contact", r.message);
					}
				}
			});
		} else {
			vmraid.model.set_value(cdt, cdn, "customer_contact", "");
		}
	}
});
