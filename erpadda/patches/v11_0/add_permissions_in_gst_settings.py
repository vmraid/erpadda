import vmraid

from erpadda.regional.india.setup import add_permissions


def execute():
	company = vmraid.get_all("Company", filters={"country": "India"})
	if not company:
		return

	vmraid.reload_doc("regional", "doctype", "lower_deduction_certificate")
	vmraid.reload_doc("regional", "doctype", "gstr_3b_report")
	add_permissions()
