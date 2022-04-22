// Copyright (c) 2019, VMRaid and contributors
// For license information, please see license.txt

vmraid.ui.form.on('Process Loan Security Shortfall', {
	onload: function(frm) {
		frm.set_value('update_time', vmraid.datetime.now_datetime());
	}
});
