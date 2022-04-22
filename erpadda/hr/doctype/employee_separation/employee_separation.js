// Copyright (c) 2018, VMRaid and contributors
// For license information, please see license.txt

vmraid.ui.form.on('Employee Separation', {
	setup: function(frm) {
		frm.add_fetch("employee_separation_template", "company", "company");
		frm.add_fetch("employee_separation_template", "department", "department");
		frm.add_fetch("employee_separation_template", "designation", "designation");
		frm.add_fetch("employee_separation_template", "employee_grade", "employee_grade");
	},

	refresh: function(frm) {
		if (frm.doc.employee) {
			frm.add_custom_button(__('Employee'), function() {
				vmraid.set_route("Form", "Employee", frm.doc.employee);
			},__("View"));
		}
		if (frm.doc.project) {
			frm.add_custom_button(__('Project'), function() {
				vmraid.set_route("Form", "Project", frm.doc.project);
			},__("View"));
			frm.add_custom_button(__('Task'), function() {
				vmraid.set_route('List', 'Task', {project: frm.doc.project});
			},__("View"));
		}
	},

	employee_separation_template: function(frm) {
		frm.set_value("activities" ,"");
		if (frm.doc.employee_separation_template) {
			vmraid.call({
				method: "erpadda.controllers.employee_boarding_controller.get_onboarding_details",
				args: {
					"parent": frm.doc.employee_separation_template,
					"parenttype": "Employee Separation Template"
				},
				callback: function(r) {
					if (r.message) {
						$.each(r.message, function(i, d) {
							var row = vmraid.model.add_child(frm.doc, "Employee Boarding Activity", "activities");
							$.extend(row, d);
						});
					}
					refresh_field("activities");
				}
			});
		}
	}
});
