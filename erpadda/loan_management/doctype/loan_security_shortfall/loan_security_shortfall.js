// Copyright (c) 2019, VMRaid and contributors
// For license information, please see license.txt

vmraid.ui.form.on('Loan Security Shortfall', {
	refresh: function(frm) {
		frm.add_custom_button(__("Add Loan Security"), function() {
			frm.trigger('shortfall_action');
		});
	},

	shortfall_action: function(frm) {
		vmraid.call({
			method: "erpadda.loan_management.doctype.loan_security_shortfall.loan_security_shortfall.add_security",
			args: {
				'loan': frm.doc.loan
			},
			callback: function(r) {
				if (r.message) {
					let doc = vmraid.model.sync(r.message)[0];
					vmraid.set_route("Form", doc.doctype, doc.name);
				}
			}
		});
	}
});
