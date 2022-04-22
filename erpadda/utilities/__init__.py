## temp utility

import vmraid
from vmraid.utils import cstr

from erpadda.utilities.activation import get_level


def update_doctypes():
	for d in vmraid.db.sql(
		"""select df.parent, df.fieldname
		from tabDocField df, tabDocType dt where df.fieldname
		like "%description%" and df.parent = dt.name and dt.istable = 1""",
		as_dict=1,
	):
		dt = vmraid.get_doc("DocType", d.parent)

		for f in dt.fields:
			if f.fieldname == d.fieldname and f.fieldtype in ("Text", "Small Text"):
				f.fieldtype = "Text Editor"
				dt.save()
				break


def get_site_info(site_info):
	# called via hook
	company = vmraid.db.get_single_value("Global Defaults", "default_company")
	domain = None

	if not company:
		company = vmraid.db.sql("select name from `tabCompany` order by creation asc")
		company = company[0][0] if company else None

	if company:
		domain = vmraid.get_cached_value("Company", cstr(company), "domain")

	return {"company": company, "domain": domain, "activation": get_level()}
