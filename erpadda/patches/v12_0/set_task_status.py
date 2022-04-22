import vmraid


def execute():
	vmraid.reload_doctype("Task")

	# add "Completed" if customized
	property_setter_name = vmraid.db.exists(
		"Property Setter", dict(doc_type="Task", field_name="status", property="options")
	)
	if property_setter_name:
		property_setter = vmraid.get_doc("Property Setter", property_setter_name)
		if not "Completed" in property_setter.value:
			property_setter.value = property_setter.value + "\nCompleted"
			property_setter.save()

	# renamed default status to Completed as status "Closed" is ambiguous
	vmraid.db.sql('update tabTask set status = "Completed" where status = "Closed"')
