# Copyright (c) 2015, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt

import vmraid

# test_records = vmraid.get_test_records('Designation')


def create_designation(**args):
	args = vmraid._dict(args)
	if vmraid.db.exists("Designation", args.designation_name or "_Test designation"):
		return vmraid.get_doc("Designation", args.designation_name or "_Test designation")

	designation = vmraid.get_doc(
		{
			"doctype": "Designation",
			"designation_name": args.designation_name or "_Test designation",
			"description": args.description or "_Test description",
		}
	)
	designation.save()
	return designation
