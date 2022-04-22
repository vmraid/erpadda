# Copyright (c) 2017, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid

from erpadda.regional.italy.setup import add_permissions


def execute():
	countries = vmraid.get_all("Company", fields="country")
	countries = [country["country"] for country in countries]
	if "Italy" in countries:
		add_permissions()
