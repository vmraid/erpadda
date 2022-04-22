# Copyright (c) 2015, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


from erpadda.controllers.trends import get_columns, get_data


def execute(filters=None):
	if not filters:
		filters = {}
	data = []
	conditions = get_columns(filters, "Sales Invoice")
	data = get_data(filters, conditions)

	return conditions["columns"], data
