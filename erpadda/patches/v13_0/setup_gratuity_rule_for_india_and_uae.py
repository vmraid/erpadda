# Copyright (c) 2019, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid


def execute():
	vmraid.reload_doc("payroll", "doctype", "gratuity_rule")
	vmraid.reload_doc("payroll", "doctype", "gratuity_rule_slab")
	vmraid.reload_doc("payroll", "doctype", "gratuity_applicable_component")
	if vmraid.db.exists("Company", {"country": "India"}):
		from erpadda.regional.india.setup import create_gratuity_rule

		create_gratuity_rule()
	if vmraid.db.exists("Company", {"country": "United Arab Emirates"}):
		from erpadda.regional.united_arab_emirates.setup import create_gratuity_rule

		create_gratuity_rule()
