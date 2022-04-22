// Copyright (c) 2015, VMRaid and Contributors
// License: GNU General Public License v3. See license.txt

vmraid.provide("erpadda.stock");

erpadda.stock.StockController = class StockController extends vmraid.ui.form.Controller {
	onload() {
		// warehouse query if company
		if (this.frm.fields_dict.company) {
			this.setup_warehouse_query();
		}
	}

	setup_warehouse_query() {
		var me = this;
		erpadda.queries.setup_queries(this.frm, "Warehouse", function() {
			return erpadda.queries.warehouse(me.frm.doc);
		});
	}

	setup_posting_date_time_check() {
		// make posting date default and read only unless explictly checked
		vmraid.ui.form.on(this.frm.doctype, 'set_posting_date_and_time_read_only', function(frm) {
			if(frm.doc.docstatus == 0 && frm.doc.set_posting_time) {
				frm.set_df_property('posting_date', 'read_only', 0);
				frm.set_df_property('posting_time', 'read_only', 0);
			} else {
				frm.set_df_property('posting_date', 'read_only', 1);
				frm.set_df_property('posting_time', 'read_only', 1);
			}
		})

		vmraid.ui.form.on(this.frm.doctype, 'set_posting_time', function(frm) {
			frm.trigger('set_posting_date_and_time_read_only');
		});

		vmraid.ui.form.on(this.frm.doctype, 'refresh', function(frm) {
			// set default posting date / time
			if(frm.doc.docstatus==0) {
				if(!frm.doc.posting_date) {
					frm.set_value('posting_date', vmraid.datetime.nowdate());
				}
				if(!frm.doc.posting_time) {
					frm.set_value('posting_time', vmraid.datetime.now_time());
				}
				frm.trigger('set_posting_date_and_time_read_only');
			}
		});
	}

	show_stock_ledger() {
		var me = this;
		if(this.frm.doc.docstatus > 0) {
			cur_frm.add_custom_button(__("Stock Ledger"), function() {
				vmraid.route_options = {
					voucher_no: me.frm.doc.name,
					from_date: me.frm.doc.posting_date,
					to_date: moment(me.frm.doc.modified).format('YYYY-MM-DD'),
					company: me.frm.doc.company,
					show_cancelled_entries: me.frm.doc.docstatus === 2
				};
				vmraid.set_route("query-report", "Stock Ledger");
			}, __("View"));
		}

	}

	show_general_ledger() {
		var me = this;
		if(this.frm.doc.docstatus > 0) {
			cur_frm.add_custom_button(__('Accounting Ledger'), function() {
				vmraid.route_options = {
					voucher_no: me.frm.doc.name,
					from_date: me.frm.doc.posting_date,
					to_date: moment(me.frm.doc.modified).format('YYYY-MM-DD'),
					company: me.frm.doc.company,
					group_by: "Group by Voucher (Consolidated)",
					show_cancelled_entries: me.frm.doc.docstatus === 2
				};
				vmraid.set_route("query-report", "General Ledger");
			}, __("View"));
		}
	}
};
