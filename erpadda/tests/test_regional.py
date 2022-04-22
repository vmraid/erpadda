import unittest

import vmraid

import erpadda


@erpadda.allow_regional
def test_method():
	return "original"


class TestInit(unittest.TestCase):
	def test_regional_overrides(self):
		vmraid.flags.country = "India"
		self.assertEqual(test_method(), "overridden")

		vmraid.flags.country = "Maldives"
		self.assertEqual(test_method(), "original")

		vmraid.flags.country = "France"
		self.assertEqual(test_method(), "overridden")
