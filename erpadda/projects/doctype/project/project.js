// Copyright (c) 2015, VMRaid and Contributors
// License: GNU General Public License v3. See license.txt
vmraid.ui.form.on("Project", {
	setup(frm) {
		frm.make_methods = {
			'Timesheet': () => {
				open_form(frm, "Timesheet", "Timesheet Detail", "time_logs");
			},
			'Purchase Order': () => {
				open_form(frm, "Purchase Order", "Purchase Order Item", "items");
			},
			'Purchase Receipt': () => {
				open_form(frm, "Purchase Receipt", "Purchase Receipt Item", "items");
			},
			'Purchase Invoice': () => {
				open_form(frm, "Purchase Invoice", "Purchase Invoice Item", "items");
			},
		};
	},
	onload: function (frm) {
		const so = frm.get_docfield("sales_order");
		so.get_route_options_for_new_doc = () => {
			if (frm.is_new()) return;
			return {
				"customer": frm.doc.customer,
				"project_name": frm.doc.name
			};
		};

		frm.set_query('customer', 'erpadda.controllers.queries.customer_query');

		frm.set_query("user", "users", function () {
			return {
				query: "erpadda.projects.doctype.project.project.get_users_for_project"
			};
		});

		// sales order
		frm.set_query('sales_order', function () {
			var filters = {
				'project': ["in", frm.doc.__islocal ? [""] : [frm.doc.name, ""]]
			};

			if (frm.doc.customer) {
				filters["customer"] = frm.doc.customer;
			}

			return {
				filters: filters
			};
		});
	},

	refresh: function (frm) {
		if (frm.doc.__islocal) {
			frm.web_link && frm.web_link.remove();
		} else {
			frm.add_web_link("/projects?project=" + encodeURIComponent(frm.doc.name));

			frm.trigger('show_dashboard');
		}
		frm.trigger("set_custom_buttons");
	},

	set_custom_buttons: function(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__('Duplicate Project with Tasks'), () => {
				frm.events.create_duplicate(frm);
			}, __("Actions"));

			frm.trigger("set_project_status_button");


			if (vmraid.model.can_read("Task")) {
				frm.add_custom_button(__("Gantt Chart"), function () {
					vmraid.route_options = {
						"project": frm.doc.name
					};
					vmraid.set_route("List", "Task", "Gantt");
				}, __("View"));

				frm.add_custom_button(__("Kanban Board"), () => {
					vmraid.call('erpadda.projects.doctype.project.project.create_kanban_board_if_not_exists', {
						project: frm.doc.name
					}).then(() => {
						vmraid.set_route('List', 'Task', 'Kanban', frm.doc.project_name);
					});
				}, __("View"));
			}
		}


	},

	set_project_status_button: function(frm) {
		frm.add_custom_button(__('Set Project Status'), () => {
			let d = new vmraid.ui.Dialog({
				"title": __("Set Project Status"),
				"fields": [
					{
						"fieldname": "status",
						"fieldtype": "Select",
						"label": "Status",
						"reqd": 1,
						"options": "Completed\nCancelled",
					},
				],
				primary_action: function() {
					frm.events.set_status(frm, d.get_values().status);
					d.hide();
				},
				primary_action_label: __("Set Project Status")
			}).show();
		}, __("Actions"));
	},

	create_duplicate: function(frm) {
		return new Promise(resolve => {
			vmraid.prompt('Project Name', (data) => {
				vmraid.xcall('erpadda.projects.doctype.project.project.create_duplicate_project',
					{
						prev_doc: frm.doc,
						project_name: data.value
					}).then(() => {
					vmraid.set_route('Form', "Project", data.value);
					vmraid.show_alert(__("Duplicate project has been created"));
				});
				resolve();
			});
		});
	},

	set_status: function(frm, status) {
		vmraid.confirm(__('Set Project and all Tasks to status {0}?', [status.bold()]), () => {
			vmraid.xcall('erpadda.projects.doctype.project.project.set_project_status',
				{project: frm.doc.name, status: status}).then(() => {
				frm.reload_doc();
			});
		});
	},

});

function open_form(frm, doctype, child_doctype, parentfield) {
	vmraid.model.with_doctype(doctype, () => {
		let new_doc = vmraid.model.get_new_doc(doctype);

		// add a new row and set the project
		let new_child_doc = vmraid.model.get_new_doc(child_doctype);
		new_child_doc.project = frm.doc.name;
		new_child_doc.parent = new_doc.name;
		new_child_doc.parentfield = parentfield;
		new_child_doc.parenttype = doctype;
		new_doc[parentfield] = [new_child_doc];

		vmraid.ui.form.make_quick_entry(doctype, null, null, new_doc);
	});

}
