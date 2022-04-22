# Copyright (c) 2018, VMRaid and Contributors
# See license.txt

import unittest

import vmraid


class TestLeavePolicy(unittest.TestCase):
	def test_max_leave_allowed(self):
		random_leave_type = vmraid.get_all("Leave Type", fields=["name", "max_leaves_allowed"])
		if random_leave_type:
			random_leave_type = random_leave_type[0]
			leave_type = vmraid.get_doc("Leave Type", random_leave_type.name)
			leave_type.max_leaves_allowed = 2
			leave_type.save()

		leave_policy = create_leave_policy(
			leave_type=leave_type.name, annual_allocation=leave_type.max_leaves_allowed + 1
		)

		self.assertRaises(vmraid.ValidationError, leave_policy.insert)


def create_leave_policy(**args):
	"""Returns an object of leave policy"""
	args = vmraid._dict(args)
	return vmraid.get_doc(
		{
			"doctype": "Leave Policy",
			"title": "Test Leave Policy",
			"leave_policy_details": [
				{
					"leave_type": args.leave_type or "_Test Leave Type",
					"annual_allocation": args.annual_allocation or 10,
				}
			],
		}
	)
