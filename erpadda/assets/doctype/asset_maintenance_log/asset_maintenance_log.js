// Copyright (c) 2017, VMRaid and contributors
// For license information, please see license.txt

vmraid.ui.form.on('Asset Maintenance Log', {
	asset_maintenance: (frm) => {
		frm.set_query('task', function(doc) {
			return {
				query: "erpadda.assets.doctype.asset_maintenance_log.asset_maintenance_log.get_maintenance_tasks",
				filters: {
					'asset_maintenance': doc.asset_maintenance
				}
			};
		});
	}
});
