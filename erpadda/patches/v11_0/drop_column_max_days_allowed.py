import vmraid


def execute():
	if vmraid.db.exists("DocType", "Leave Type"):
		if "max_days_allowed" in vmraid.db.get_table_columns("Leave Type"):
			vmraid.db.sql("alter table `tabLeave Type` drop column max_days_allowed")
