import vmraid


def execute():

	company = vmraid.get_all("Company", filters={"country": "India"})
	if not company:
		return

	vmraid.db.sql(
		""" UPDATE `tabSales Invoice` set gst_category = 'Unregistered'
        where gst_category = 'Registered Regular'
        and ifnull(customer_gstin, '')=''
        and ifnull(billing_address_gstin,'')=''
    """
	)

	vmraid.db.sql(
		""" UPDATE `tabPurchase Invoice` set gst_category = 'Unregistered'
        where gst_category = 'Registered Regular'
        and ifnull(supplier_gstin, '')=''
    """
	)
