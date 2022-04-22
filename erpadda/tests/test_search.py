import unittest

import vmraid
from vmraid.contacts.address_and_contact import filter_dynamic_link_doctypes


class TestSearch(unittest.TestCase):
	# Search for the word "cond", part of the word "conduire" (Lead) in french.
	def test_contact_search_in_foreign_language(self):
		try:
			vmraid.local.lang = "fr"
			output = filter_dynamic_link_doctypes(
				"DocType", "cond", "name", 0, 20, {"fieldtype": "HTML", "fieldname": "contact_html"}
			)
			result = [["found" for x in y if x == "Lead"] for y in output]
			self.assertTrue(["found"] in result)
		finally:
			vmraid.local.lang = "en"
