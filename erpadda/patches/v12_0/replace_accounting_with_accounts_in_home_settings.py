import vmraid


def execute():
	vmraid.db.sql(
		"""UPDATE `tabUser` SET `home_settings` = REPLACE(`home_settings`, 'Accounting', 'Accounts')"""
	)
	vmraid.cache().delete_key("home_settings")
