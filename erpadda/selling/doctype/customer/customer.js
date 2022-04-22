// Copyright (c) 2015, VMRaid and Contributors
// License: GNU General Public License v3. See license.txt

vmraid.ui.form.on("Customer", {
	setup: function(frm) {

		frm.make_methods = {
			'Quotation': () => vmraid.model.open_mapped_doc({
				method: "erpadda.selling.doctype.customer.customer.make_quotation",
				frm: cur_frm
			}),
			'Opportunity': () => vmraid.model.open_mapped_doc({
				method: "erpadda.selling.doctype.customer.customer.make_opportunity",
				frm: cur_frm
			})
		}

		frm.add_fetch('lead_name', 'company_name', 'customer_name');
		frm.add_fetch('default_sales_partner','commission_rate','default_commission_rate');
		frm.set_query('customer_group', {'is_group': 0});
		frm.set_query('default_price_list', { 'selling': 1});
		frm.set_query('account', 'accounts', function(doc, cdt, cdn) {
			var d  = locals[cdt][cdn];
			var filters = {
				'account_type': 'Receivable',
				'company': d.company,
				"is_group": 0
			};

			if(doc.party_account_currency) {
				$.extend(filters, {"account_currency": doc.party_account_currency});
			}
			return {
				filters: filters
			}
		});

		if (frm.doc.__islocal == 1) {
			frm.set_value("represents_company", "");
		}

		frm.set_query('customer_primary_contact', function(doc) {
			return {
				query: "erpadda.selling.doctype.customer.customer.get_customer_primary_contact",
				filters: {
					'customer': doc.name
				}
			}
		})
		frm.set_query('customer_primary_address', function(doc) {
			return {
				filters: {
					'link_doctype': 'Customer',
					'link_name': doc.name
				}
			}
		})

		frm.set_query('default_bank_account', function() {
			return {
				filters: {
					'is_company_account': 1
				}
			}
		});
	},
	customer_primary_address: function(frm){
		if(frm.doc.customer_primary_address){
			vmraid.call({
				method: 'vmraid.contacts.doctype.address.address.get_address_display',
				args: {
					"address_dict": frm.doc.customer_primary_address
				},
				callback: function(r) {
					frm.set_value("primary_address", r.message);
				}
			});
		}
		if(!frm.doc.customer_primary_address){
			frm.set_value("primary_address", "");
		}
	},

	is_internal_customer: function(frm) {
		if (frm.doc.is_internal_customer == 1) {
			frm.toggle_reqd("represents_company", true);
		}
		else {
			frm.toggle_reqd("represents_company", false);
		}
	},

	customer_primary_contact: function(frm){
		if(!frm.doc.customer_primary_contact){
			frm.set_value("mobile_no", "");
			frm.set_value("email_id", "");
		}
	},

	loyalty_program: function(frm) {
		if(frm.doc.loyalty_program) {
			frm.set_value('loyalty_program_tier', null);
		}
	},

	refresh: function(frm) {
		if(vmraid.defaults.get_default("cust_master_name")!="Naming Series") {
			frm.toggle_display("naming_series", false);
		} else {
			erpadda.toggle_naming_series();
		}

		vmraid.dynamic_link = {doc: frm.doc, fieldname: 'name', doctype: 'Customer'}

		if(!frm.doc.__islocal) {
			vmraid.contacts.render_address_and_contact(frm);

			// custom buttons

			frm.add_custom_button(__('Accounts Receivable'), function () {
				vmraid.set_route('query-report', 'Accounts Receivable', {customer:frm.doc.name});
			}, __('View'));

			frm.add_custom_button(__('Accounting Ledger'), function () {
				vmraid.set_route('query-report', 'General Ledger',
					{party_type: 'Customer', party: frm.doc.name});
			}, __('View'));

			frm.add_custom_button(__('Pricing Rule'), function () {
				erpadda.utils.make_pricing_rule(frm.doc.doctype, frm.doc.name);
			}, __('Create'));

			frm.add_custom_button(__('Get Customer Group Details'), function () {
				frm.trigger("get_customer_group_details");
			}, __('Actions'));

			if (cint(vmraid.defaults.get_default("enable_common_party_accounting"))) {
				frm.add_custom_button(__('Link with Supplier'), function () {
					frm.trigger('show_party_link_dialog');
				}, __('Actions'));
			}

			// indicator
			erpadda.utils.set_party_dashboard_indicators(frm);

		} else {
			vmraid.contacts.clear_address_and_contact(frm);
		}

		var grid = cur_frm.get_field("sales_team").grid;
		grid.set_column_disp("allocated_amount", false);
		grid.set_column_disp("incentives", false);
	},
	validate: function(frm) {
		if(frm.doc.lead_name) vmraid.model.clear_doc("Lead", frm.doc.lead_name);

	},
	get_customer_group_details: function(frm) {
		vmraid.call({
			method: "get_customer_group_details",
			doc: frm.doc,
			callback: function() {
				frm.refresh();
			}
		});

	},
	show_party_link_dialog: function(frm) {
		const dialog = new vmraid.ui.Dialog({
			title: __('Select a Supplier'),
			fields: [{
				fieldtype: 'Link', label: __('Supplier'),
				options: 'Supplier', fieldname: 'supplier', reqd: 1
			}],
			primary_action: function({ supplier }) {
				vmraid.call({
					method: 'erpadda.accounts.doctype.party_link.party_link.create_party_link',
					args: {
						primary_role: 'Customer',
						primary_party: frm.doc.name,
						secondary_party: supplier
					},
					freeze: true,
					callback: function() {
						dialog.hide();
						vmraid.msgprint({
							message: __('Successfully linked to Supplier'),
							alert: true
						});
					},
					error: function() {
						dialog.hide();
						vmraid.msgprint({
							message: __('Linking to Supplier Failed. Please try again.'),
							title: __('Linking Failed'),
							indicator: 'red'
						});
					}
				});
			},
			primary_action_label: __('Create Link')
		});
		dialog.show();
	}
});
