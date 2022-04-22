// Copyright (c) 2015, VMRaid and Contributors
// License: GNU General Public License v3. See license.txt

vmraid.provide("erpadda.stock");
vmraid.provide("erpadda.accounts.dimensions");

vmraid.ui.form.on("Stock Reconciliation", {
	onload: function(frm) {
		frm.add_fetch("item_code", "item_name", "item_name");

		// end of life
		frm.set_query("item_code", "items", function(doc, cdt, cdn) {
			return {
				query: "erpadda.controllers.queries.item_query",
				filters:{
					"is_stock_item": 1
				}
			}
		});
		frm.set_query("batch_no", "items", function(doc, cdt, cdn) {
			var item = locals[cdt][cdn];
			return {
				filters: {
					'item': item.item_code
				}
			};
		});

		if (frm.doc.company) {
			erpadda.queries.setup_queries(frm, "Warehouse", function() {
				return erpadda.queries.warehouse(frm.doc);
			});
		}

		if (!frm.doc.expense_account) {
			frm.trigger("set_expense_account");
		}

		erpadda.accounts.dimensions.setup_dimension_filters(frm, frm.doctype);
	},

	company: function(frm) {
		erpadda.accounts.dimensions.update_dimension(frm, frm.doctype);
	},

	refresh: function(frm) {
		if(frm.doc.docstatus < 1) {
			frm.add_custom_button(__("Fetch Items from Warehouse"), function() {
				frm.events.get_items(frm);
			});
		}

		if(frm.doc.company) {
			frm.trigger("toggle_display_account_head");
		}
	},

	scan_barcode: function(frm) {
		const barcode_scanner = new erpadda.utils.BarcodeScanner({frm:frm});
		barcode_scanner.process_scan();
	},

	scan_mode: function(frm) {
		if (frm.doc.scan_mode) {
			vmraid.show_alert({
				message: __("Scan mode enabled, existing quantity will not be fetched."),
				indicator: "green"
			});
		}
	},

	set_warehouse: function(frm) {
		let transaction_controller = new erpadda.TransactionController({frm:frm});
		transaction_controller.autofill_warehouse(frm.doc.items, "warehouse", frm.doc.set_warehouse);
	},

	get_items: function(frm) {
		let fields = [
			{
				label: 'Warehouse',
				fieldname: 'warehouse',
				fieldtype: 'Link',
				options: 'Warehouse',
				reqd: 1,
				"get_query": function() {
					return {
						"filters": {
							"company": frm.doc.company,
						}
					};
				}
			},
			{
				label: "Item Code",
				fieldname: "item_code",
				fieldtype: "Link",
				options: "Item",
				"get_query": function() {
					return {
						"filters": {
							"disabled": 0,
						}
					};
				}
			},
			{
				label: __("Ignore Empty Stock"),
				fieldname: "ignore_empty_stock",
				fieldtype: "Check"
			}
		];

		vmraid.prompt(fields, function(data) {
			vmraid.call({
				method: "erpadda.stock.doctype.stock_reconciliation.stock_reconciliation.get_items",
				args: {
					warehouse: data.warehouse,
					posting_date: frm.doc.posting_date,
					posting_time: frm.doc.posting_time,
					company: frm.doc.company,
					item_code: data.item_code,
					ignore_empty_stock: data.ignore_empty_stock
				},
				callback: function(r) {
					if (r.exc || !r.message || !r.message.length) return;

					frm.clear_table("items");

					r.message.forEach((row) => {
						let item = frm.add_child("items");
						$.extend(item, row);

						item.qty = item.qty || 0;
						item.valuation_rate = item.valuation_rate || 0;
					});
					frm.refresh_field("items");
				}
			});
		}, __("Get Items"), __("Update"));
	},

	posting_date: function(frm) {
		frm.trigger("set_valuation_rate_and_qty_for_all_items");
	},

	posting_time: function(frm) {
		frm.trigger("set_valuation_rate_and_qty_for_all_items");
	},

	set_valuation_rate_and_qty_for_all_items: function(frm) {
		frm.doc.items.forEach(row => {
			frm.events.set_valuation_rate_and_qty(frm, row.doctype, row.name);
		});
	},

	set_valuation_rate_and_qty: function(frm, cdt, cdn) {
		var d = vmraid.model.get_doc(cdt, cdn);

		if(d.item_code && d.warehouse) {
			vmraid.call({
				method: "erpadda.stock.doctype.stock_reconciliation.stock_reconciliation.get_stock_balance_for",
				args: {
					item_code: d.item_code,
					warehouse: d.warehouse,
					posting_date: frm.doc.posting_date,
					posting_time: frm.doc.posting_time,
					batch_no: d.batch_no
				},
				callback: function(r) {
					const row = vmraid.model.get_doc(cdt, cdn);
					if (!frm.doc.scan_mode) {
						vmraid.model.set_value(cdt, cdn, "qty", r.message.qty);
					}
					vmraid.model.set_value(cdt, cdn, "valuation_rate", r.message.rate);
					vmraid.model.set_value(cdt, cdn, "current_qty", r.message.qty);
					vmraid.model.set_value(cdt, cdn, "current_valuation_rate", r.message.rate);
					vmraid.model.set_value(cdt, cdn, "current_amount", r.message.rate * r.message.qty);
					vmraid.model.set_value(cdt, cdn, "amount", row.qty * row.valuation_rate);
					vmraid.model.set_value(cdt, cdn, "current_serial_no", r.message.serial_nos);

					if (frm.doc.purpose == "Stock Reconciliation" && !frm.doc.scan_mode) {
						vmraid.model.set_value(cdt, cdn, "serial_no", r.message.serial_nos);
					}
				}
			});
		}
	},

	set_amount_quantity: function(doc, cdt, cdn) {
		var d = vmraid.model.get_doc(cdt, cdn);
		if (d.qty & d.valuation_rate) {
			vmraid.model.set_value(cdt, cdn, "amount", flt(d.qty) * flt(d.valuation_rate));
			vmraid.model.set_value(cdt, cdn, "quantity_difference", flt(d.qty) - flt(d.current_qty));
			vmraid.model.set_value(cdt, cdn, "amount_difference", flt(d.amount) - flt(d.current_amount));
		}
	},
	company: function(frm) {
		frm.trigger("toggle_display_account_head");
	},
	toggle_display_account_head: function(frm) {
		frm.toggle_display(['expense_account', 'cost_center'],
			erpadda.is_perpetual_inventory_enabled(frm.doc.company));
	},
	purpose: function(frm) {
		frm.trigger("set_expense_account");
	},
	set_expense_account: function(frm) {
		if (frm.doc.company && erpadda.is_perpetual_inventory_enabled(frm.doc.company)) {
			return frm.call({
				method: "erpadda.stock.doctype.stock_reconciliation.stock_reconciliation.get_difference_account",
				args: {
					"purpose": frm.doc.purpose,
					"company": frm.doc.company
				},
				callback: function(r) {
					if (!r.exc) {
						frm.set_value("expense_account", r.message);
					}
				}
			});
		}
	}
});

vmraid.ui.form.on("Stock Reconciliation Item", {

	warehouse: function(frm, cdt, cdn) {
		var child = locals[cdt][cdn];
		if (child.batch_no && !frm.doc.scan_mode) {
			vmraid.model.set_value(child.cdt, child.cdn, "batch_no", "");
		}

		frm.events.set_valuation_rate_and_qty(frm, cdt, cdn);
	},

	item_code: function(frm, cdt, cdn) {
		var child = locals[cdt][cdn];
		if (child.batch_no && !frm.doc.scan_mode) {
			vmraid.model.set_value(cdt, cdn, "batch_no", "");
		}

		frm.events.set_valuation_rate_and_qty(frm, cdt, cdn);
	},

	batch_no: function(frm, cdt, cdn) {
		frm.events.set_valuation_rate_and_qty(frm, cdt, cdn);
	},

	qty: function(frm, cdt, cdn) {
		frm.events.set_amount_quantity(frm, cdt, cdn);
	},

	valuation_rate: function(frm, cdt, cdn) {
		frm.events.set_amount_quantity(frm, cdt, cdn);
	},

	serial_no: function(frm, cdt, cdn) {
		var child = locals[cdt][cdn];

		if (child.serial_no) {
			const serial_nos = child.serial_no.trim().split('\n');
			vmraid.model.set_value(cdt, cdn, "qty", serial_nos.length);
		}
	},

	items_add: function(frm, cdt, cdn) {
		var item = vmraid.get_doc(cdt, cdn);
		if (!item.warehouse && frm.doc.set_warehouse) {
			vmraid.model.set_value(cdt, cdn, "warehouse", frm.doc.set_warehouse);
		}
	},

});

erpadda.stock.StockReconciliation = class StockReconciliation extends erpadda.stock.StockController {
	setup() {
		var me = this;

		this.setup_posting_date_time_check();

		if (me.frm.doc.company && erpadda.is_perpetual_inventory_enabled(me.frm.doc.company)) {
			this.frm.add_fetch("company", "cost_center", "cost_center");
		}
		this.frm.fields_dict["expense_account"].get_query = function() {
			if(erpadda.is_perpetual_inventory_enabled(me.frm.doc.company)) {
				return {
					"filters": {
						'company': me.frm.doc.company,
						"is_group": 0
					}
				}
			}
		}
		this.frm.fields_dict["cost_center"].get_query = function() {
			if(erpadda.is_perpetual_inventory_enabled(me.frm.doc.company)) {
				return {
					"filters": {
						'company': me.frm.doc.company,
						"is_group": 0
					}
				}
			}
		}
	}

	refresh() {
		if(this.frm.doc.docstatus > 0) {
			this.show_stock_ledger();
			if (erpadda.is_perpetual_inventory_enabled(this.frm.doc.company)) {
				this.show_general_ledger();
			}
		}
	}

};

cur_frm.cscript = new erpadda.stock.StockReconciliation({frm: cur_frm});
