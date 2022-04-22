import vmraid


def execute():
	vmraid.delete_doc("DocType", "Shopify Settings", ignore_missing=True)
	vmraid.delete_doc("DocType", "Shopify Log", ignore_missing=True)
