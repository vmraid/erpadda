// Copyright (c) 2018, VMRaid and contributors
// For license information, please see license.txt

vmraid.ui.form.on('Subscription Plan', {
	price_determination: function(frm) {
		frm.toggle_reqd("cost", frm.doc.price_determination === 'Fixed rate');
		frm.toggle_reqd("price_list", frm.doc.price_determination === 'Based on price list');
	}
});
