// Copyright (c) 2018, VMRaid and contributors
// For license information, please see license.txt

vmraid.ui.form.on('Project Update', {
	refresh: function() {

	},

	onload: function (frm) {
		frm.set_value("naming_series", "UPDATE-.project.-.YY.MM.DD.-.####");
	},

	validate: function (frm) {
		frm.set_value("time", vmraid.datetime.now_time());
		frm.set_value("date", vmraid.datetime.nowdate());
	}
});
