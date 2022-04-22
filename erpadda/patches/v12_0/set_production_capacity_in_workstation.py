import vmraid


def execute():
	vmraid.reload_doc("manufacturing", "doctype", "workstation")

	vmraid.db.sql(
		""" UPDATE `tabWorkstation`
        SET production_capacity = 1 """
	)
