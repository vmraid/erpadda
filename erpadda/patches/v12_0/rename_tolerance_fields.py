import vmraid
from vmraid.model.utils.rename_field import rename_field


def execute():
	vmraid.reload_doc("stock", "doctype", "item")
	vmraid.reload_doc("stock", "doctype", "stock_settings")
	vmraid.reload_doc("accounts", "doctype", "accounts_settings")

	rename_field("Stock Settings", "tolerance", "over_delivery_receipt_allowance")
	rename_field("Item", "tolerance", "over_delivery_receipt_allowance")

	qty_allowance = vmraid.db.get_single_value("Stock Settings", "over_delivery_receipt_allowance")
	vmraid.db.set_value("Accounts Settings", None, "over_delivery_receipt_allowance", qty_allowance)

	vmraid.db.sql("update tabItem set over_billing_allowance=over_delivery_receipt_allowance")
