import vmraid

from erpadda.regional.india.setup import make_custom_fields


def execute():

	company = vmraid.get_all("Company", filters={"country": "India"})
	if not company:
		return

	vmraid.reload_doc("accounts", "doctype", "Tax Category")

	make_custom_fields()

	for doctype in ["Sales Invoice", "Purchase Invoice"]:
		has_column = vmraid.db.has_column(doctype, "invoice_type")

		if has_column:
			update_map = {
				"Regular": "Registered Regular",
				"Export": "Overseas",
				"SEZ": "SEZ",
				"Deemed Export": "Deemed Export",
			}

			for old, new in update_map.items():
				vmraid.db.sql(
					"UPDATE `tab{doctype}` SET gst_category = %s where invoice_type = %s".format(doctype=doctype),
					(new, old),
				)  # nosec

	vmraid.delete_doc("Custom Field", "Sales Invoice-invoice_type")
	vmraid.delete_doc("Custom Field", "Purchase Invoice-invoice_type")

	itc_update_map = {
		"ineligible": "Ineligible",
		"input service": "Input Service Distributor",
		"capital goods": "Import Of Capital Goods",
		"input": "All Other ITC",
	}

	has_gst_fields = vmraid.db.has_column("Purchase Invoice", "eligibility_for_itc")

	if has_gst_fields:
		for old, new in itc_update_map.items():
			vmraid.db.sql(
				"UPDATE `tabPurchase Invoice` SET eligibility_for_itc = %s where eligibility_for_itc = %s ",
				(new, old),
			)

	for doctype in ["Customer", "Supplier"]:

		vmraid.db.sql(
			""" UPDATE `tab{doctype}` t1, `tabAddress` t2, `tabDynamic Link` t3 SET t1.gst_category = "Registered Regular"
			where t3.link_name = t1.name and t3.parent = t2.name and t2.gstin IS NOT NULL and t2.gstin != '' """.format(
				doctype=doctype
			)
		)  # nosec

		vmraid.db.sql(
			""" UPDATE `tab{doctype}` t1, `tabAddress` t2, `tabDynamic Link` t3 SET t1.gst_category = "Overseas"
			where t3.link_name = t1.name and t3.parent = t2.name and t2.country != 'India' """.format(
				doctype=doctype
			)
		)  # nosec
