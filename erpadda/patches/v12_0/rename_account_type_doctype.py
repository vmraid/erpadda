import vmraid


def execute():
	vmraid.rename_doc("DocType", "Account Type", "Bank Account Type", force=True)
	vmraid.rename_doc("DocType", "Account Subtype", "Bank Account Subtype", force=True)
	vmraid.reload_doc("accounts", "doctype", "bank_account")
