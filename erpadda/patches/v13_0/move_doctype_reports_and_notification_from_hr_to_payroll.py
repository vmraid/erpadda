# Copyright (c) 2019, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid


def execute():
	vmraid.db.sql(
		"""UPDATE `tabPrint Format`
        SET module = 'Payroll'
        WHERE name IN ('Salary Slip Based On Timesheet', 'Salary Slip Standard')"""
	)

	vmraid.db.sql("""UPDATE `tabNotification` SET module='Payroll' WHERE name='Retention Bonus';""")

	doctypes_moved = [
		"Employee Benefit Application Detail",
		"Employee Tax Exemption Declaration Category",
		"Salary Component",
		"Employee Tax Exemption Proof Submission Detail",
		"Income Tax Slab Other Charges",
		"Taxable Salary Slab",
		"Payroll Period Date",
		"Salary Slip Timesheet",
		"Payroll Employee Detail",
		"Salary Detail",
		"Employee Tax Exemption Sub Category",
		"Employee Tax Exemption Category",
		"Employee Benefit Claim",
		"Employee Benefit Application",
		"Employee Other Income",
		"Employee Tax Exemption Proof Submission",
		"Employee Tax Exemption Declaration",
		"Employee Incentive",
		"Retention Bonus",
		"Additional Salary",
		"Income Tax Slab",
		"Payroll Period",
		"Salary Slip",
		"Payroll Entry",
		"Salary Structure Assignment",
		"Salary Structure",
	]

	for doctype in doctypes_moved:
		vmraid.delete_doc_if_exists("DocType", doctype)

	reports = ["Salary Register", "Bank Remittance"]

	for report in reports:
		vmraid.delete_doc_if_exists("Report", report)
