# Copyright (c) 2019, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid

from erpadda.setup.install import add_non_standard_user_types


def execute():
	doctype_dict = {
		"projects": ["Timesheet"],
		"payroll": [
			"Salary Slip",
			"Employee Tax Exemption Declaration",
			"Employee Tax Exemption Proof Submission",
			"Employee Benefit Application",
			"Employee Benefit Claim",
		],
		"hr": [
			"Employee",
			"Expense Claim",
			"Leave Application",
			"Attendance Request",
			"Compensatory Leave Request",
			"Holiday List",
			"Employee Advance",
			"Training Program",
			"Training Feedback",
			"Shift Request",
			"Employee Grievance",
			"Employee Referral",
			"Travel Request",
		],
	}

	for module, doctypes in doctype_dict.items():
		for doctype in doctypes:
			vmraid.reload_doc(module, "doctype", doctype)

	vmraid.flags.ignore_select_perm = True
	vmraid.flags.update_select_perm_after_migrate = True

	add_non_standard_user_types()
