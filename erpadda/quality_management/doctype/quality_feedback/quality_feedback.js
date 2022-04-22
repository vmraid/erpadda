// Copyright (c) 2019, VMRaid and contributors
// For license information, please see license.txt

vmraid.ui.form.on('Quality Feedback', {
	template: function(frm) {
		if (frm.doc.template) {
			frm.call('set_parameters');
		}
	}
});
