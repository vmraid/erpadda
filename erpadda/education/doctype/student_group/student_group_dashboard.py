# Copyright (c) 2020, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt

from vmraid import _


def get_data():
	return {
		"fieldname": "student_group",
		"transactions": [
			{"label": _("Assessment"), "items": ["Assessment Plan", "Assessment Result"]},
			{"label": _("Course"), "items": ["Course Schedule"]},
		],
	}
