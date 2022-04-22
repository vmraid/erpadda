import vmraid


def execute():
	vmraid.reload_doctype("Employee")
	vmraid.db.sql("update tabEmployee set first_name = employee_name")

	# update holiday list
	vmraid.reload_doctype("Holiday List")
	for holiday_list in vmraid.get_all("Holiday List"):
		holiday_list = vmraid.get_doc("Holiday List", holiday_list.name)
		holiday_list.db_set("total_holidays", len(holiday_list.holidays), update_modified=False)
