# Copyright (c) 2015, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid
from vmraid import scrub
from vmraid.model.utils.rename_field import rename_field


def execute():
	for doctype in ("Salary Component", "Salary Detail"):
		if "depends_on_lwp" in vmraid.db.get_table_columns(doctype):
			vmraid.reload_doc("Payroll", "doctype", scrub(doctype))
			rename_field(doctype, "depends_on_lwp", "depends_on_payment_days")
