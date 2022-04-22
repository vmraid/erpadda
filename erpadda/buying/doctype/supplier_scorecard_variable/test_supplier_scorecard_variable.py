# Copyright (c) 2017, VMRaid and Contributors
# See license.txt


import vmraid
from vmraid.tests.utils import VMRaidTestCase

from erpadda.buying.doctype.supplier_scorecard_variable.supplier_scorecard_variable import (
	VariablePathNotFound,
)


class TestSupplierScorecardVariable(VMRaidTestCase):
	def test_variable_exist(self):
		for d in test_existing_variables:
			my_doc = vmraid.get_doc("Supplier Scorecard Variable", d.get("name"))
			self.assertEqual(my_doc.param_name, d.get("param_name"))
			self.assertEqual(my_doc.variable_label, d.get("variable_label"))
			self.assertEqual(my_doc.path, d.get("path"))

	def test_path_exists(self):
		for d in test_good_variables:
			if vmraid.db.exists(d):
				vmraid.delete_doc(d.get("doctype"), d.get("name"))
			vmraid.get_doc(d).insert()

		for d in test_bad_variables:
			self.assertRaises(VariablePathNotFound, vmraid.get_doc(d).insert)


test_existing_variables = [
	{
		"param_name": "total_accepted_items",
		"name": "Total Accepted Items",
		"doctype": "Supplier Scorecard Variable",
		"variable_label": "Total Accepted Items",
		"path": "get_total_accepted_items",
	},
]

test_good_variables = [
	{
		"param_name": "good_variable1",
		"name": "Good Variable 1",
		"doctype": "Supplier Scorecard Variable",
		"variable_label": "Good Variable 1",
		"path": "get_total_accepted_items",
	},
]

test_bad_variables = [
	{
		"param_name": "fake_variable1",
		"name": "Fake Variable 1",
		"doctype": "Supplier Scorecard Variable",
		"variable_label": "Fake Variable 1",
		"path": "get_fake_variable1",
	},
]