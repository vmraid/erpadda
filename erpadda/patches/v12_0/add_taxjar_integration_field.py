import vmraid

from erpadda.regional.united_states.setup import make_custom_fields


def execute():
	company = vmraid.get_all("Company", filters={"country": "United States"})
	if not company:
		return

	make_custom_fields()
