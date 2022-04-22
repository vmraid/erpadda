import vmraid
from vmraid.model.utils.rename_field import rename_field


def execute():
	vmraid.reload_doc("Healthcare", "doctype", "Inpatient Record")
	if vmraid.db.has_column("Inpatient Record", "discharge_date"):
		rename_field("Inpatient Record", "discharge_date", "discharge_datetime")
