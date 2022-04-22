import vmraid

from erpadda.regional.india.setup import add_custom_roles_for_reports


def execute():
	company = vmraid.get_all("Company", filters={"country": "India"})
	if not company:
		return

	add_custom_roles_for_reports()
