import vmraid


def execute():
	vmraid.reload_doctype("Buying Settings")
	buying_settings = vmraid.get_single("Buying Settings")
	buying_settings.bill_for_rejected_quantity_in_purchase_invoice = 0
	buying_settings.save()
