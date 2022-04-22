# Copyright (c) 2017, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


from datetime import datetime

import vmraid
from vmraid.utils import getdate

from erpadda.payroll.doctype.salary_structure_assignment.salary_structure_assignment import (
	DuplicateAssignment,
)


def execute():
	vmraid.reload_doc("Payroll", "doctype", "Salary Structure")
	vmraid.reload_doc("Payroll", "doctype", "Salary Structure Assignment")
	vmraid.db.sql(
		"""
		delete from `tabSalary Structure Assignment`
		where salary_structure in (select name from `tabSalary Structure` where is_active='No' or docstatus!=1)
	"""
	)
	if vmraid.db.table_exists("Salary Structure Employee"):
		ss_details = vmraid.db.sql(
			"""
			select sse.employee, sse.employee_name, sse.from_date, sse.to_date,
				sse.base, sse.variable, sse.parent as salary_structure, ss.company
			from `tabSalary Structure Employee` sse, `tabSalary Structure` ss
			where ss.name = sse.parent AND ss.is_active='Yes'
			AND sse.employee in (select name from `tabEmployee` where ifNull(status, '') != 'Left')""",
			as_dict=1,
		)
	else:
		cols = ""
		if "base" in vmraid.db.get_table_columns("Salary Structure"):
			cols = ", base, variable"

		ss_details = vmraid.db.sql(
			"""
			select name as salary_structure, employee, employee_name, from_date, to_date, company {0}
			from `tabSalary Structure`
			where is_active='Yes'
			AND employee in (select name from `tabEmployee` where ifNull(status, '') != 'Left')
		""".format(
				cols
			),
			as_dict=1,
		)

	all_companies = vmraid.db.get_all("Company", fields=["name", "default_currency"])
	for d in all_companies:
		company = d.name
		company_currency = d.default_currency

		vmraid.db.sql(
			"""update `tabSalary Structure` set currency = %s where company=%s""",
			(company_currency, company),
		)

	for d in ss_details:
		try:
			joining_date, relieving_date = vmraid.db.get_value(
				"Employee", d.employee, ["date_of_joining", "relieving_date"]
			)
			from_date = d.from_date
			if joining_date and getdate(from_date) < joining_date:
				from_date = joining_date
			elif relieving_date and getdate(from_date) > relieving_date:
				continue
			company_currency = vmraid.db.get_value("Company", d.company, "default_currency")

			s = vmraid.new_doc("Salary Structure Assignment")
			s.employee = d.employee
			s.employee_name = d.employee_name
			s.salary_structure = d.salary_structure
			s.from_date = from_date
			s.to_date = d.to_date if isinstance(d.to_date, datetime) else None
			s.base = d.get("base")
			s.variable = d.get("variable")
			s.company = d.company
			s.currency = company_currency

			# to migrate the data of the old employees
			s.flags.old_employee = True
			s.save()
			s.submit()
		except DuplicateAssignment:
			pass

	vmraid.db.sql("update `tabSalary Structure` set docstatus=1")
