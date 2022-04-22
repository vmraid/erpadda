import unittest

import vmraid

from erpadda import encode_company_abbr

test_records = vmraid.get_test_records("Company")


class TestInit(unittest.TestCase):
	def test_encode_company_abbr(self):

		abbr = "NFECT"

		names = [
			"Warehouse Name",
			"ERPAdda Foundation India",
			"Gold - Member - {a}".format(a=abbr),
			" - {a}".format(a=abbr),
			"ERPAdda - Foundation - India",
			"ERPAdda Foundation India - {a}".format(a=abbr),
			"No-Space-{a}".format(a=abbr),
			"- Warehouse",
		]

		expected_names = [
			"Warehouse Name - {a}".format(a=abbr),
			"ERPAdda Foundation India - {a}".format(a=abbr),
			"Gold - Member - {a}".format(a=abbr),
			" - {a}".format(a=abbr),
			"ERPAdda - Foundation - India - {a}".format(a=abbr),
			"ERPAdda Foundation India - {a}".format(a=abbr),
			"No-Space-{a} - {a}".format(a=abbr),
			"- Warehouse - {a}".format(a=abbr),
		]

		for i in range(len(names)):
			enc_name = encode_company_abbr(names[i], abbr=abbr)
			self.assertTrue(
				enc_name == expected_names[i],
				"{enc} is not same as {exp}".format(enc=enc_name, exp=expected_names[i]),
			)
