import vmraid


def execute():
	vmraid.reload_doc("non_profit", "doctype", "member")
	old_named_members = vmraid.get_all("Member", filters={"name": ("not like", "MEM-%")})
	correctly_named_members = vmraid.get_all("Member", filters={"name": ("like", "MEM-%")})
	current_index = len(correctly_named_members)

	for member in old_named_members:
		current_index += 1
		vmraid.rename_doc("Member", member["name"], "MEM-" + str(current_index).zfill(5))

	vmraid.db.sql("""update `tabMember` set naming_series = 'MEM-'""")
