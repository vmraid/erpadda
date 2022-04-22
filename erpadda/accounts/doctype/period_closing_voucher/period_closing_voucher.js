// Copyright (c) 2015, VMRaid and Contributors
// License: GNU General Public License v3. See license.txt

vmraid.ui.form.on('Period Closing Voucher', {
	onload: function(frm) {
		if (!frm.doc.transaction_date) frm.doc.transaction_date = vmraid.datetime.obj_to_str(new Date());
	},

	setup: function(frm) {
		frm.set_query("closing_account_head", function() {
			return {
				filters: [
					['Account', 'company', '=', frm.doc.company],
					['Account', 'is_group', '=', '0'],
					['Account', 'freeze_account', '=', 'No'],
					['Account', 'root_type', 'in', 'Liability, Equity']
				]
			}
		});
	},

	refresh: function(frm) {
		if(frm.doc.docstatus > 0) {
			frm.add_custom_button(__('Ledger'), function() {
				vmraid.route_options = {
					"voucher_no": frm.doc.name,
					"from_date": frm.doc.posting_date,
					"to_date": moment(frm.doc.modified).format('YYYY-MM-DD'),
					"company": frm.doc.company,
					"group_by": "",
					"show_cancelled_entries": frm.doc.docstatus === 2
				};
				vmraid.set_route("query-report", "General Ledger");
			}, "fa fa-table");
		}
	}

})
