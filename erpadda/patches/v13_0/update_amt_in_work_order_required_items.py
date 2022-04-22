import vmraid


def execute():
	"""Correct amount in child table of required items table."""

	vmraid.reload_doc("manufacturing", "doctype", "work_order")
	vmraid.reload_doc("manufacturing", "doctype", "work_order_item")

	vmraid.db.sql("""UPDATE `tabWork Order Item` SET amount = rate * required_qty""")
