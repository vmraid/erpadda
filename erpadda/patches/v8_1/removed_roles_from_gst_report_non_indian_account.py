# Copyright (c) 2017, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid


def execute():
	vmraid.reload_doc("core", "doctype", "has_role")
	company = vmraid.get_all("Company", filters={"country": "India"})

	if not company:
		vmraid.db.sql(
			"""
			delete from
				`tabHas Role`
			where
				parenttype = 'Report' and parent in('GST Sales Register',
					'GST Purchase Register', 'GST Itemised Sales Register',
					'GST Itemised Purchase Register', 'Eway Bill')"""
		)
