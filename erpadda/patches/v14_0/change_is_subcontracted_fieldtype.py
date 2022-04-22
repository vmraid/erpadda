# Copyright (c) 2022, VMRaid and contributors
# For license information, please see license.txt

import vmraid


def execute():
	for doctype in ["Purchase Order", "Purchase Receipt", "Purchase Invoice", "Supplier Quotation"]:
		vmraid.db.sql(
			"""
				UPDATE `tab{doctype}`
				SET is_subcontracted = 0
				where is_subcontracted in ('', 'No') or is_subcontracted is null""".format(
				doctype=doctype
			)
		)
		vmraid.db.sql(
			"""
				UPDATE `tab{doctype}`
				SET is_subcontracted = 1
				where is_subcontracted = 'Yes'""".format(
				doctype=doctype
			)
		)

		vmraid.reload_doc(vmraid.get_meta(doctype).module, "doctype", vmraid.scrub(doctype))
