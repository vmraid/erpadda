import vmraid


def execute():
	vmraid.delete_doc("DocType", "Amazon MWS Settings", ignore_missing=True)
