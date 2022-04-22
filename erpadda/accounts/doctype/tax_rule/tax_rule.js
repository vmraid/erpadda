// Copyright (c) 2015, VMRaid and Contributors
// License: GNU General Public License v3. See license.txt

vmraid.ui.form.on("Tax Rule", "customer", function(frm) {
	if(frm.doc.customer) {
		vmraid.call({
			method:"erpadda.accounts.doctype.tax_rule.tax_rule.get_party_details",
			args: {
				"party": frm.doc.customer,
				"party_type": "customer"
			},
			callback: function(r) {
				if(!r.exc) {
					$.each(r.message, function(k, v) {
						frm.set_value(k, v);
					});
				}
			}
		});
	}
});

vmraid.ui.form.on("Tax Rule", "supplier", function(frm) {
	if(frm.doc.supplier) {
		vmraid.call({
			method:"erpadda.accounts.doctype.tax_rule.tax_rule.get_party_details",
			args: {
				"party": frm.doc.supplier,
				"party_type": "supplier"
			},
			callback: function(r) {
				if(!r.exc) {
					$.each(r.message, function(k, v) {
						frm.set_value(k, v);
					});
				}
			}
		});
	}
});
