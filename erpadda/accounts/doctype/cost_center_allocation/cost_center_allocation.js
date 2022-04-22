// Copyright (c) 2022, VMRaid and contributors
// For license information, please see license.txt

vmraid.ui.form.on('Cost Center Allocation', {
	setup: function(frm) {
		let filters = {"is_group": 0};
		if (frm.doc.company) {
			$.extend(filters, {
				"company": frm.doc.company
			});
		}

		frm.set_query('main_cost_center', function() {
			return {
				filters: filters
			};
		});
	}
});
