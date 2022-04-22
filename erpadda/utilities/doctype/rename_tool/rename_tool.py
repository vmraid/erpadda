# Copyright (c) 2015, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt

# For license information, please see license.txt


import vmraid
from vmraid.model.document import Document
from vmraid.model.rename_doc import bulk_rename


class RenameTool(Document):
	pass


@vmraid.whitelist()
def get_doctypes():
	return vmraid.db.sql_list(
		"""select name from tabDocType
		where allow_rename=1 and module!='Core' order by name"""
	)


@vmraid.whitelist()
def upload(select_doctype=None, rows=None):
	from vmraid.utils.csvutils import read_csv_content_from_attached_file

	if not select_doctype:
		select_doctype = vmraid.form_dict.select_doctype

	if not vmraid.has_permission(select_doctype, "write"):
		raise vmraid.PermissionError

	rows = read_csv_content_from_attached_file(vmraid.get_doc("Rename Tool", "Rename Tool"))

	return bulk_rename(select_doctype, rows=rows)
