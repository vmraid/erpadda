# Copyright (c) 2020, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt

from vmraid import _


def get_data():
	return {
		"fieldname": "enrollment",
		"transactions": [{"label": _("Activity"), "items": ["Course Activity", "Quiz Activity"]}],
	}
