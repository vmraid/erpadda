# Copyright (c) 2015, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid

page_title = "Partners"


def get_context(context):
	partners = vmraid.db.sql(
		"""select * from `tabSales Partner`
			where show_in_website=1 order by name asc""",
		as_dict=True,
	)

	return {"partners": partners, "title": page_title}
