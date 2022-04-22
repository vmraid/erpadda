// Copyright (c) 2016, VMRaid and contributors
// For license information, please see license.txt

vmraid.ui.form.on("Vehicle Log", {
	refresh: function(frm) {
		if(frm.doc.docstatus == 1) {
			frm.add_custom_button(__('Expense Claim'), function() {
				frm.events.expense_claim(frm);
			}, __('Create'));
			frm.page.set_inner_btn_group_as_primary(__('Create'));
		}
	},

	expense_claim: function(frm){
		vmraid.call({
			method: "erpadda.hr.doctype.vehicle_log.vehicle_log.make_expense_claim",
			args:{
				docname: frm.doc.name
			},
			callback: function(r){
				var doc = vmraid.model.sync(r.message);
				vmraid.set_route('Form', 'Expense Claim', r.message.name);
			}
		});
	}
});
