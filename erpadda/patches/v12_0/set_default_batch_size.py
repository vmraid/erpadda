import vmraid


def execute():
	vmraid.reload_doc("manufacturing", "doctype", "bom_operation")
	vmraid.reload_doc("manufacturing", "doctype", "work_order_operation")

	vmraid.db.sql(
		"""
        UPDATE
            `tabBOM Operation` bo
        SET
            bo.batch_size = 1
    """
	)
	vmraid.db.sql(
		"""
        UPDATE
            `tabWork Order Operation` wop
        SET
            wop.batch_size = 1
    """
	)
