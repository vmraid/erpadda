import vmraid


def execute():

	doctypes = vmraid.get_all("DocType", {"module": "Hub Node", "custom": 0}, pluck="name")
	for doctype in doctypes:
		vmraid.delete_doc("DocType", doctype, ignore_missing=True)

	vmraid.delete_doc("Module Def", "Hub Node", ignore_missing=True, force=True)
