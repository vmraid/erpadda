// Copyright (c) 2015, VMRaid and Contributors
// License: GNU General Public License v3. See license.txt

vmraid.ui.form.on('Mode of Payment', {
	setup: function(frm) {
		frm.set_query("default_account", "accounts", function(doc, cdt, cdn) {
			let d = locals[cdt][cdn];
			return {
				filters: [
					['Account', 'account_type', 'in', 'Bank, Cash, Receivable'],
					['Account', 'is_group', '=', 0],
					['Account', 'company', '=', d.company]
				]
			};
		});
	},
});
