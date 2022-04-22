// Copyright (c) 2021, VMRaid and contributors
// For license information, please see license.txt

vmraid.ui.form.on('South Africa VAT Settings', {
	refresh: function(frm) {
		frm.set_query("company", function() {
			return {
				filters: {
					country: "South Africa",
				}
			};
		});
		frm.set_query("account", "vat_accounts", function() {
			return {
				filters: {
					company: frm.doc.company,
					account_type: "Tax",
					is_group: 0
				}
			};
		});
	}
});
