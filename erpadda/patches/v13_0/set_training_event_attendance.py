import vmraid


def execute():
	vmraid.reload_doc("hr", "doctype", "training_event")
	vmraid.reload_doc("hr", "doctype", "training_event_employee")

	vmraid.db.sql("update `tabTraining Event Employee` set `attendance` = 'Present'")
	vmraid.db.sql(
		"update `tabTraining Event Employee` set `is_mandatory` = 1 where `attendance` = 'Mandatory'"
	)
