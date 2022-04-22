// Copyright (c) 2020, VMRaid and contributors
// For license information, please see license.txt

vmraid.ui.form.on('Mpesa Settings', {
	onload_post_render: function(frm) {
		frm.events.setup_account_balance_html(frm);
	},

	refresh: function(frm) {
		vmraid.realtime.on("refresh_mpesa_dashboard", function(){
			frm.reload_doc();
			frm.events.setup_account_balance_html(frm);
		});
	},

	get_account_balance: function(frm) {
		if (!frm.doc.initiator_name && !frm.doc.security_credential) {
			vmraid.throw(__("Please set the initiator name and the security credential"));
		}
		vmraid.call({
			method: "get_account_balance_info",
			doc: frm.doc
		});
	},

	setup_account_balance_html: function(frm) {
		if (!frm.doc.account_balance) return;
		$("div").remove(".form-dashboard-section.custom");
		frm.dashboard.add_section(
			vmraid.render_template('account_balance', {
				data: JSON.parse(frm.doc.account_balance)
			})
		);
		frm.dashboard.show();
	}

});
