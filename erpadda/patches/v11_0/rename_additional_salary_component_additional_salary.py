import vmraid

# this patch should have been included with this PR https://github.com/vmraid/erpadda/pull/14302


def execute():
	if vmraid.db.table_exists("Additional Salary Component"):
		if not vmraid.db.table_exists("Additional Salary"):
			vmraid.rename_doc("DocType", "Additional Salary Component", "Additional Salary")

		vmraid.delete_doc("DocType", "Additional Salary Component")
