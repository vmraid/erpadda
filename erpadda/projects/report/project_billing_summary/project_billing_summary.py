# Copyright (c) 2013, VMRaid and contributors
# For license information, please see license.txt


import vmraid

from erpadda.projects.report.billing_summary import get_columns, get_data


def execute(filters=None):
	filters = vmraid._dict(filters or {})
	columns = get_columns()

	data = get_data(filters)
	return columns, data
