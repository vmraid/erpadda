import vmraid


def execute():
	if vmraid.db.exists("DocType", "Membership"):
		if "webhook_payload" in vmraid.db.get_table_columns("Membership"):
			vmraid.db.sql("alter table `tabMembership` drop column webhook_payload")
