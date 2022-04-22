vmraid.treeview_settings['Employee'] = {
	get_tree_nodes: "erpadda.hr.doctype.employee.employee.get_children",
	filters: [
		{
			fieldname: "company",
			fieldtype:"Select",
			options: ['All Companies'].concat(erpadda.utils.get_tree_options("company")),
			label: __("Company"),
			default: erpadda.utils.get_tree_default("company")
		}
	],
	breadcrumb: "Hr",
	disable_add_node: true,
	get_tree_root: false,
	toolbar: [
		{ toggle_btn: true },
		{
			label:__("Edit"),
			condition: function(node) {
				return !node.is_root;
			},
			click: function(node) {
				vmraid.set_route("Form", "Employee", node.data.value);
			}
		}
	],
	menu_items: [
		{
			label: __("New Employee"),
			action: function() {
				vmraid.new_doc("Employee", true);
			},
			condition: 'vmraid.boot.user.can_create.indexOf("Employee") !== -1'
		}
	],
};
