# Copyright (c) 2020, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt

from vmraid import _


def get_data():
	return {
		"fieldname": "room",
		"transactions": [
			{"label": _("Course"), "items": ["Course Schedule"]},
			{"label": _("Assessment"), "items": ["Assessment Plan"]},
		],
	}
