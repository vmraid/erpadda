import vmraid


def execute():
	vmraid.db.sql(
		"""
		update tabCustomer
		set represents_company = NULL
		where represents_company = ''
	"""
	)
