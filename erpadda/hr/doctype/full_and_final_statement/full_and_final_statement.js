// Copyright (c) 2021, VMRaid and contributors
// For license information, please see license.txt

vmraid.ui.form.on('Full and Final Statement', {
	refresh: function(frm) {
		frm.events.set_queries(frm, "payables");
		frm.events.set_queries(frm, "receivables");

		if (frm.doc.docstatus == 1 && frm.doc.status == "Unpaid") {
			frm.add_custom_button(__("Create Journal Entry"), function () {
				frm.events.create_journal_entry(frm);
			});
		}
	},

	set_queries: function(frm, type) {
		frm.set_query("reference_document_type", type, function () {
			let modules = ["HR", "Payroll", "Loan Management"];
			return {
				filters: {
					istable: 0,
					issingle: 0,
					module: ["In", modules]
				}
			};
		});

		let filters = {};

		frm.set_query('reference_document', type, function(doc, cdt, cdn) {
			let fnf_doc = vmraid.get_doc(cdt, cdn);

			vmraid.model.with_doctype(fnf_doc.reference_document_type, function() {
				if (vmraid.model.is_tree(fnf_doc.reference_document_type)) {
					filters['is_group'] = 0;
				}

				if (vmraid.meta.has_field(fnf_doc.reference_document_type, 'company')) {
					filters['company'] = frm.doc.company;
				}

				if (vmraid.meta.has_field(fnf_doc.reference_document_type, 'employee')) {
					filters['employee'] = frm.doc.employee;
				}
			});

			return {
				filters: filters
			};
		});
	},

	employee: function(frm) {
		frm.events.get_outstanding_statements(frm);
	},

	get_outstanding_statements: function(frm) {
		if (frm.doc.employee) {
			vmraid.call({
				method: "get_outstanding_statements",
				doc: frm.doc,
				callback: function() {
					frm.refresh();
				}
			});
		}
	},

	create_journal_entry: function(frm) {
		vmraid.call({
			method: "create_journal_entry",
			doc: frm.doc,
			callback: function(r) {
				var doclist = vmraid.model.sync(r.message);
				vmraid.set_route("Form", doclist[0].doctype, doclist[0].name);
			}
		});
	}
});

vmraid.ui.form.on("Full and Final Outstanding Statement", {
	reference_document: function(frm, cdt, cdn) {
		var child = locals[cdt][cdn];
		if (child.reference_document_type && child.reference_document) {
			vmraid.call({
				method: "erpadda.hr.doctype.full_and_final_statement.full_and_final_statement.get_account_and_amount",
				args: {
					ref_doctype: child.reference_document_type,
					ref_document: child.reference_document
				},
				callback: function(r) {
					if (r.message) {
						vmraid.model.set_value(cdt, cdn, "account", r.message[0]);
						vmraid.model.set_value(cdt, cdn, "amount", r.message[1]);
					}
				}
			});
		}
	},

	amount: function(frm) {
		var total_payable_amount = 0;
		var total_receivable_amount = 0;

		frm.doc.payables.forEach(element => {
			total_payable_amount = total_payable_amount + element.amount;
		});

		frm.doc.receivables.forEach(element => {
			total_receivable_amount = total_receivable_amount + element.amount;
		});
		frm.set_value("total_payable_amount", flt(total_payable_amount));
		frm.set_value("total_receivable_amount", flt(total_receivable_amount));
	}
});
