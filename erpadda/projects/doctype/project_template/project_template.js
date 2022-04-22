// Copyright (c) 2019, VMRaid and contributors
// For license information, please see license.txt

vmraid.ui.form.on('Project Template', {
	// refresh: function(frm) {

	// }
	setup: function (frm) {
		frm.set_query("task", "tasks", function () {
			return {
				filters: {
					"is_template": 1
				}
			};
		});
	}
});

vmraid.ui.form.on('Project Template Task', {
	task: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		vmraid.db.get_value("Task", row.task, "subject", (value) => {
			row.subject = value.subject;
			refresh_field("tasks");
		});
	}
});
