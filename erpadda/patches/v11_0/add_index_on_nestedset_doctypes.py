# Copyright (c) 2015, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid


def execute():
	vmraid.reload_doc("assets", "doctype", "Location")
	for dt in (
		"Account",
		"Cost Center",
		"File",
		"Employee",
		"Location",
		"Task",
		"Customer Group",
		"Sales Person",
		"Territory",
	):
		vmraid.reload_doctype(dt)
		vmraid.get_doc("DocType", dt).run_module_method("on_doctype_update")
