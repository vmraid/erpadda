# Copyright (c) 2018, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid

from erpadda.setup.doctype.company.company import install_country_fixtures


def execute():
	vmraid.reload_doc("regional", "report", "fichier_des_ecritures_comptables_[fec]")
	for d in vmraid.get_all("Company", filters={"country": "France"}):
		install_country_fixtures(d.name)
