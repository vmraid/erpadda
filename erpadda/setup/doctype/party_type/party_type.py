# Copyright (c) 2015, VMRaid Technologies and contributors
# For license information, please see license.txt


import vmraid
from vmraid.model.document import Document


class PartyType(Document):
	pass


@vmraid.whitelist()
@vmraid.validate_and_sanitize_search_inputs
def get_party_type(doctype, txt, searchfield, start, page_len, filters):
	cond = ""
	if filters and filters.get("account"):
		account_type = vmraid.db.get_value("Account", filters.get("account"), "account_type")
		cond = "and account_type = '%s'" % account_type

	return vmraid.db.sql(
		"""select name from `tabParty Type`
			where `{key}` LIKE %(txt)s {cond}
			order by name limit %(start)s, %(page_len)s""".format(
			key=searchfield, cond=cond
		),
		{"txt": "%" + txt + "%", "start": start, "page_len": page_len},
	)
