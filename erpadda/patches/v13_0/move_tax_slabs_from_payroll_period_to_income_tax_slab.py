# Copyright (c) 2019, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid


def execute():
	if not (
		vmraid.db.table_exists("Payroll Period") and vmraid.db.table_exists("Taxable Salary Slab")
	):
		return

	for doctype in (
		"income_tax_slab",
		"salary_structure_assignment",
		"employee_other_income",
		"income_tax_slab_other_charges",
	):
		vmraid.reload_doc("Payroll", "doctype", doctype)

	standard_tax_exemption_amount_exists = vmraid.db.has_column(
		"Payroll Period", "standard_tax_exemption_amount"
	)

	select_fields = "name, start_date, end_date"
	if standard_tax_exemption_amount_exists:
		select_fields = "name, start_date, end_date, standard_tax_exemption_amount"

	for company in vmraid.get_all("Company"):
		payroll_periods = vmraid.db.sql(
			"""
			SELECT
				{0}
			FROM
				`tabPayroll Period`
			WHERE company=%s
			ORDER BY start_date DESC
		""".format(
				select_fields
			),
			company.name,
			as_dict=1,
		)

		for i, period in enumerate(payroll_periods):
			income_tax_slab = vmraid.new_doc("Income Tax Slab")
			income_tax_slab.name = "Tax Slab:" + period.name

			if i == 0:
				income_tax_slab.disabled = 0
			else:
				income_tax_slab.disabled = 1

			income_tax_slab.effective_from = period.start_date
			income_tax_slab.company = company.name
			income_tax_slab.allow_tax_exemption = 1
			if standard_tax_exemption_amount_exists:
				income_tax_slab.standard_tax_exemption_amount = period.standard_tax_exemption_amount

			income_tax_slab.flags.ignore_mandatory = True
			income_tax_slab.submit()

			vmraid.db.sql(
				""" UPDATE `tabTaxable Salary Slab`
				SET parent = %s , parentfield = 'slabs' , parenttype = "Income Tax Slab"
				WHERE parent = %s
			""",
				(income_tax_slab.name, period.name),
				as_dict=1,
			)

			if i == 0:
				vmraid.db.sql(
					"""
					UPDATE
						`tabSalary Structure Assignment`
					set
						income_tax_slab = %s
					where
						company = %s
						and from_date >= %s
						and docstatus < 2
				""",
					(income_tax_slab.name, company.name, period.start_date),
				)

	# move other incomes to separate document
	if not vmraid.db.table_exists("Employee Tax Exemption Proof Submission"):
		return

	migrated = []
	proofs = vmraid.get_all(
		"Employee Tax Exemption Proof Submission",
		filters={"docstatus": 1},
		fields=["payroll_period", "employee", "company", "income_from_other_sources"],
	)
	for proof in proofs:
		if proof.income_from_other_sources:
			employee_other_income = vmraid.new_doc("Employee Other Income")
			employee_other_income.employee = proof.employee
			employee_other_income.payroll_period = proof.payroll_period
			employee_other_income.company = proof.company
			employee_other_income.amount = proof.income_from_other_sources

			try:
				employee_other_income.submit()
				migrated.append([proof.employee, proof.payroll_period])
			except Exception:
				pass

	if not vmraid.db.table_exists("Employee Tax Exemption Declaration"):
		return

	declerations = vmraid.get_all(
		"Employee Tax Exemption Declaration",
		filters={"docstatus": 1},
		fields=["payroll_period", "employee", "company", "income_from_other_sources"],
	)

	for declaration in declerations:
		if (
			declaration.income_from_other_sources
			and [declaration.employee, declaration.payroll_period] not in migrated
		):
			employee_other_income = vmraid.new_doc("Employee Other Income")
			employee_other_income.employee = declaration.employee
			employee_other_income.payroll_period = declaration.payroll_period
			employee_other_income.company = declaration.company
			employee_other_income.amount = declaration.income_from_other_sources

			try:
				employee_other_income.submit()
			except Exception:
				pass
