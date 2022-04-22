# Copyright (c) 2017, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid


def execute():
	vmraid.db.sql(
		"""
		DELETE FROM `tabProperty Setter`
		WHERE doc_type in ('Sales Invoice', 'Purchase Invoice', 'Payment Entry')
		AND field_name = 'cost_center'
		AND property = 'hidden'
	"""
	)
