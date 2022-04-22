# Copyright (c) 2015, VMRaid and Contributors
# See license.txt

import unittest

import vmraid

test_records = vmraid.get_test_records("Operation")


class TestOperation(unittest.TestCase):
	pass


def make_operation(*args, **kwargs):
	args = args if args else kwargs
	if isinstance(args, tuple):
		args = args[0]

	args = vmraid._dict(args)

	if not vmraid.db.exists("Operation", args.operation):
		doc = vmraid.get_doc(
			{"doctype": "Operation", "name": args.operation, "workstation": args.workstation}
		)
		doc.insert()
		return doc

	return vmraid.get_doc("Operation", args.operation)
