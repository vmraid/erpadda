vmraid.treeview_settings["Location"] = {
	ignore_fields: ["parent_location"],
	get_tree_nodes: 'erpadda.assets.doctype.location.location.get_children',
	add_tree_node: 'erpadda.assets.doctype.location.location.add_node',
	filters: [
		{
			fieldname: "location",
			fieldtype: "Link",
			options: "Location",
			label: __("Location"),
			get_query: function () {
				return {
					filters: [["Location", "is_group", "=", 1]]
				};
			}
		},
	],
	breadcrumb: "Assets",
	root_label: "All Locations",
	get_tree_root: false,
	menu_items: [
		{
			label: __("New Location"),
			action: function () {
				vmraid.new_doc("Location", true);
			},
			condition: 'vmraid.boot.user.can_create.indexOf("Location") !== -1'
		}
	],
	onload: function (treeview) {
		treeview.make_tree();
	}
};
