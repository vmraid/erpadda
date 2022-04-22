import vmraid


def execute():
	if vmraid.db.exists("DocType", "Member"):
		vmraid.reload_doc("Non Profit", "doctype", "Member")

		if vmraid.db.has_column("Member", "subscription_activated"):
			vmraid.db.sql(
				'UPDATE `tabMember` SET subscription_status = "Active" WHERE subscription_activated = 1'
			)
			vmraid.db.sql_ddl("ALTER table `tabMember` DROP COLUMN subscription_activated")
