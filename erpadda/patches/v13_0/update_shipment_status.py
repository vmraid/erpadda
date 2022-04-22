import vmraid


def execute():
	vmraid.reload_doc("stock", "doctype", "shipment")

	# update submitted status
	vmraid.db.sql(
		"""UPDATE `tabShipment`
					SET status = "Submitted"
					WHERE status = "Draft" AND docstatus = 1"""
	)

	# update cancelled status
	vmraid.db.sql(
		"""UPDATE `tabShipment`
					SET status = "Cancelled"
					WHERE status = "Draft" AND docstatus = 2"""
	)
