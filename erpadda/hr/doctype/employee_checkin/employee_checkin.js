// Copyright (c) 2019, VMRaid and contributors
// For license information, please see license.txt

vmraid.ui.form.on('Employee Checkin', {
	setup: (frm) => {
		if(!frm.doc.time) {
			frm.set_value("time", vmraid.datetime.now_datetime());
		}
	}
});
