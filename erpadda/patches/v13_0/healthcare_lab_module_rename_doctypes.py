import vmraid
from vmraid.model.utils.rename_field import rename_field


def execute():
	if vmraid.db.exists("DocType", "Lab Test") and vmraid.db.exists("DocType", "Lab Test Template"):
		# rename child doctypes
		doctypes = {
			"Lab Test Groups": "Lab Test Group Template",
			"Normal Test Items": "Normal Test Result",
			"Sensitivity Test Items": "Sensitivity Test Result",
			"Special Test Items": "Descriptive Test Result",
			"Special Test Template": "Descriptive Test Template",
		}

		vmraid.reload_doc("healthcare", "doctype", "lab_test")
		vmraid.reload_doc("healthcare", "doctype", "lab_test_template")

		for old_dt, new_dt in doctypes.items():
			vmraid.flags.link_fields = {}
			should_rename = vmraid.db.table_exists(old_dt) and not vmraid.db.table_exists(new_dt)
			if should_rename:
				vmraid.reload_doc("healthcare", "doctype", vmraid.scrub(old_dt))
				vmraid.rename_doc("DocType", old_dt, new_dt, force=True)
				vmraid.reload_doc("healthcare", "doctype", vmraid.scrub(new_dt))
				vmraid.delete_doc_if_exists("DocType", old_dt)

		parent_fields = {
			"Lab Test Group Template": "lab_test_groups",
			"Descriptive Test Template": "descriptive_test_templates",
			"Normal Test Result": "normal_test_items",
			"Sensitivity Test Result": "sensitivity_test_items",
			"Descriptive Test Result": "descriptive_test_items",
		}

		for doctype, parentfield in parent_fields.items():
			vmraid.db.sql(
				"""
				UPDATE `tab{0}`
				SET parentfield = %(parentfield)s
			""".format(
					doctype
				),
				{"parentfield": parentfield},
			)

		# copy renamed child table fields (fields were already renamed in old doctype json, hence sql)
		rename_fields = {
			"lab_test_name": "test_name",
			"lab_test_event": "test_event",
			"lab_test_uom": "test_uom",
			"lab_test_comment": "test_comment",
		}

		for new, old in rename_fields.items():
			if vmraid.db.has_column("Normal Test Result", old):
				vmraid.db.sql("""UPDATE `tabNormal Test Result` SET {} = {}""".format(new, old))

		if vmraid.db.has_column("Normal Test Template", "test_event"):
			vmraid.db.sql("""UPDATE `tabNormal Test Template` SET lab_test_event = test_event""")

		if vmraid.db.has_column("Normal Test Template", "test_uom"):
			vmraid.db.sql("""UPDATE `tabNormal Test Template` SET lab_test_uom = test_uom""")

		if vmraid.db.has_column("Descriptive Test Result", "test_particulars"):
			vmraid.db.sql(
				"""UPDATE `tabDescriptive Test Result` SET lab_test_particulars = test_particulars"""
			)

		rename_fields = {
			"lab_test_template": "test_template",
			"lab_test_description": "test_description",
			"lab_test_rate": "test_rate",
		}

		for new, old in rename_fields.items():
			if vmraid.db.has_column("Lab Test Group Template", old):
				vmraid.db.sql("""UPDATE `tabLab Test Group Template` SET {} = {}""".format(new, old))

		# rename field
		vmraid.reload_doc("healthcare", "doctype", "lab_test")
		if vmraid.db.has_column("Lab Test", "special_toggle"):
			rename_field("Lab Test", "special_toggle", "descriptive_toggle")

	if vmraid.db.exists("DocType", "Lab Test Group Template"):
		# fix select field option
		vmraid.reload_doc("healthcare", "doctype", "lab_test_group_template")
		vmraid.db.sql(
			"""
			UPDATE `tabLab Test Group Template`
			SET template_or_new_line = 'Add New Line'
			WHERE template_or_new_line = 'Add new line'
		"""
		)
