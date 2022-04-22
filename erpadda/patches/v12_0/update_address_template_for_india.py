# Copyright (c) 2020, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid

from erpadda.regional.address_template.setup import set_up_address_templates


def execute():
	if vmraid.db.get_value("Company", {"country": "India"}, "name"):
		address_template = vmraid.db.get_value("Address Template", "India", "template")
		if not address_template or "gstin" not in address_template:
			set_up_address_templates(default_country="India")
