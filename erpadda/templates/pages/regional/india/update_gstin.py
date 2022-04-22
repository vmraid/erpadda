import vmraid


def get_context(context):
	context.no_cache = 1
	party = vmraid.form_dict.party
	context.party_name = party

	try:
		update_gstin(context)
	except vmraid.ValidationError:
		context.invalid_gstin = 1

	party_type = "Customer"
	party_name = vmraid.db.get_value("Customer", party)

	if not party_name:
		party_type = "Supplier"
		party_name = vmraid.db.get_value("Supplier", party)

	if not party_name:
		context.not_found = 1
		return

	context.party = vmraid.get_doc(party_type, party_name)
	context.party.onload()


def update_gstin(context):
	dirty = False
	for key, value in vmraid.form_dict.items():
		if key != "party":
			address_name = vmraid.get_value("Address", key)
			if address_name:
				address = vmraid.get_doc("Address", address_name)
				address.gstin = value.upper()
				address.save(ignore_permissions=True)
				dirty = True

	if dirty:
		vmraid.db.commit()
		context.updated = True
