import vmraid
from vmraid import _
from vmraid.model.utils.rename_field import rename_field
from vmraid.utils.nestedset import rebuild_tree


def execute():
	if vmraid.db.table_exists("Supplier Group"):
		vmraid.reload_doc("setup", "doctype", "supplier_group")
	elif vmraid.db.table_exists("Supplier Type"):
		vmraid.rename_doc("DocType", "Supplier Type", "Supplier Group", force=True)
		vmraid.reload_doc("setup", "doctype", "supplier_group")
		vmraid.reload_doc("accounts", "doctype", "pricing_rule")
		vmraid.reload_doc("accounts", "doctype", "tax_rule")
		vmraid.reload_doc("buying", "doctype", "buying_settings")
		vmraid.reload_doc("buying", "doctype", "supplier")
		rename_field("Supplier Group", "supplier_type", "supplier_group_name")
		rename_field("Supplier", "supplier_type", "supplier_group")
		rename_field("Buying Settings", "supplier_type", "supplier_group")
		rename_field("Pricing Rule", "supplier_type", "supplier_group")
		rename_field("Tax Rule", "supplier_type", "supplier_group")

	build_tree()


def build_tree():
	vmraid.db.sql(
		"""update `tabSupplier Group` set parent_supplier_group = '{0}'
		where is_group = 0""".format(
			_("All Supplier Groups")
		)
	)

	if not vmraid.db.exists("Supplier Group", _("All Supplier Groups")):
		vmraid.get_doc(
			{
				"doctype": "Supplier Group",
				"supplier_group_name": _("All Supplier Groups"),
				"is_group": 1,
				"parent_supplier_group": "",
			}
		).insert(ignore_permissions=True)

	rebuild_tree("Supplier Group", "parent_supplier_group")
