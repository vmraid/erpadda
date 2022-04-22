# Copyright (c) 2020, VMRaid and contributors
# For license information, please see license.txt


import vmraid
from vmraid.model.document import Document


class JournalEntryTemplate(Document):
	pass


@vmraid.whitelist()
def get_naming_series():
	return vmraid.get_meta("Journal Entry").get_field("naming_series").options
