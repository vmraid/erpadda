// Copyright (c) 2018, VMRaid and contributors
// For license information, please see license.txt

vmraid.ui.form.on('Daily Work Summary Group', {
	refresh: function (frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__('Daily Work Summary'), function () {
				vmraid.set_route('List', 'Daily Work Summary');
			});
		}
	}
});
