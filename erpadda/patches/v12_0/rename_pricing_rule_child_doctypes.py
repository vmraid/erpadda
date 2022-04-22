# Copyright (c) 2017, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid

doctypes = {
	"Price Discount Slab": "Promotional Scheme Price Discount",
	"Product Discount Slab": "Promotional Scheme Product Discount",
	"Apply Rule On Item Code": "Pricing Rule Item Code",
	"Apply Rule On Item Group": "Pricing Rule Item Group",
	"Apply Rule On Brand": "Pricing Rule Brand",
}


def execute():
	for old_doc, new_doc in doctypes.items():
		if not vmraid.db.table_exists(new_doc) and vmraid.db.table_exists(old_doc):
			vmraid.rename_doc("DocType", old_doc, new_doc)
			vmraid.reload_doc("accounts", "doctype", vmraid.scrub(new_doc))
			vmraid.delete_doc("DocType", old_doc)
