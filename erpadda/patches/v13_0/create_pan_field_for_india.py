import vmraid
from vmraid.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	vmraid.reload_doc("buying", "doctype", "supplier", force=True)
	vmraid.reload_doc("selling", "doctype", "customer", force=True)
	vmraid.reload_doc("core", "doctype", "doctype", force=True)

	custom_fields = {
		"Supplier": [
			{"fieldname": "pan", "label": "PAN", "fieldtype": "Data", "insert_after": "supplier_type"}
		],
		"Customer": [
			{"fieldname": "pan", "label": "PAN", "fieldtype": "Data", "insert_after": "customer_type"}
		],
	}

	create_custom_fields(custom_fields, update=True)
