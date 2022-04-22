import vmraid


def execute():
	company = vmraid.get_all("Company", filters={"country": "India"})
	if not company:
		return

	vmraid.reload_doc("regional", "doctype", "lower_deduction_certificate")

	ldc = vmraid.qb.DocType("Lower Deduction Certificate").as_("ldc")
	supplier = vmraid.qb.DocType("Supplier")

	vmraid.qb.update(ldc).inner_join(supplier).on(ldc.supplier == supplier.name).set(
		ldc.tax_withholding_category, supplier.tax_withholding_category
	).where(ldc.tax_withholding_category.isnull()).run()
