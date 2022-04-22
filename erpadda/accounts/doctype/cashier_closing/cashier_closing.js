// Copyright (c) 2015, VMRaid and Contributors
// License: GNU General Public License v3. See license.txt

vmraid.ui.form.on('Cashier Closing', {

	setup: function(frm){
		if (frm.doc.user == "" || frm.doc.user == null) {
			frm.doc.user = vmraid.session.user;
		}
	}
});
