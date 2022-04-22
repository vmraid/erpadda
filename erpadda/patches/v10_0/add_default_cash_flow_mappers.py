# Copyright (c) 2017, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid

from erpadda.setup.install import create_default_cash_flow_mapper_templates


def execute():
	vmraid.reload_doc("accounts", "doctype", vmraid.scrub("Cash Flow Mapping"))
	vmraid.reload_doc("accounts", "doctype", vmraid.scrub("Cash Flow Mapper"))
	vmraid.reload_doc("accounts", "doctype", vmraid.scrub("Cash Flow Mapping Template Details"))

	create_default_cash_flow_mapper_templates()
