import vmraid


def execute():
	if "Education" in vmraid.get_active_domains() and not vmraid.db.exists("Role", "Guardian"):
		doc = vmraid.new_doc("Role")
		doc.update({"role_name": "Guardian", "desk_access": 0})

		doc.insert(ignore_permissions=True)
