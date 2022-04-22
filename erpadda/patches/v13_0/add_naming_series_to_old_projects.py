import vmraid


def execute():
	vmraid.reload_doc("projects", "doctype", "project")

	vmraid.db.sql(
		"""UPDATE `tabProject`
		SET
			naming_series = 'PROJ-.####'
		WHERE
			naming_series is NULL"""
	)
