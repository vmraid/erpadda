import vmraid

from erpadda.selling.doctype.sales_order.sales_order import update_produced_qty_in_so_item


def execute():
	vmraid.reload_doctype("Sales Order Item")
	vmraid.reload_doctype("Sales Order")

	for d in vmraid.get_all(
		"Work Order",
		fields=["sales_order", "sales_order_item"],
		filters={"sales_order": ("!=", ""), "sales_order_item": ("!=", "")},
	):

		# update produced qty in sales order
		update_produced_qty_in_so_item(d.sales_order, d.sales_order_item)
