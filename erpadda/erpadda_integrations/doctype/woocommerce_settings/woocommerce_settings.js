// Copyright (c) 2018, VMRaid and contributors
// For license information, please see license.txt

vmraid.ui.form.on('Woocommerce Settings', {
	refresh (frm) {
		frm.trigger("add_button_generate_secret");
		frm.trigger("check_enabled");
		frm.set_query("tax_account", ()=>{
			return {
				"filters": {
					"company": vmraid.defaults.get_default("company"),
					"is_group": 0
				}
			};
		});
	},

	enable_sync (frm) {
		frm.trigger("check_enabled");
	},

	add_button_generate_secret(frm) {
		frm.add_custom_button(__('Generate Secret'), () => {
			vmraid.confirm(
				__("Apps using current key won't be able to access, are you sure?"),
				() => {
					vmraid.call({
						type:"POST",
						method:"erpadda.erpadda_integrations.doctype.woocommerce_settings.woocommerce_settings.generate_secret",
					}).done(() => {
						frm.reload_doc();
					}).fail(() => {
						vmraid.msgprint(__("Could not generate Secret"));
					});
				}
			);
		});
	},

	check_enabled (frm) {
		frm.set_df_property("woocommerce_server_url", "reqd", frm.doc.enable_sync);
		frm.set_df_property("api_consumer_key", "reqd", frm.doc.enable_sync);
		frm.set_df_property("api_consumer_secret", "reqd", frm.doc.enable_sync);
	}
});

vmraid.ui.form.on("Woocommerce Settings", "onload", function () {
	vmraid.call({
		method: "erpadda.erpadda_integrations.doctype.woocommerce_settings.woocommerce_settings.get_series",
		callback: function (r) {
			$.each(r.message, function (key, value) {
				set_field_options(key, value);
			});
		}
	});
});
