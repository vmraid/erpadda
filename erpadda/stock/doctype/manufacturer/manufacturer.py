# Copyright (c) 2015, VMRaid and contributors
# For license information, please see license.txt


from vmraid.contacts.address_and_contact import load_address_and_contact
from vmraid.model.document import Document


class Manufacturer(Document):
	def onload(self):
		"""Load address and contacts in `__onload`"""
		load_address_and_contact(self)
