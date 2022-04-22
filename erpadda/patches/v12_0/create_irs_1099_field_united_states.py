import vmraid

from erpadda.regional.united_states.setup import make_custom_fields


def execute():

	vmraid.reload_doc("accounts", "doctype", "allowed_to_transact_with", force=True)
	vmraid.reload_doc("accounts", "doctype", "pricing_rule_detail", force=True)
	vmraid.reload_doc("crm", "doctype", "lost_reason_detail", force=True)
	vmraid.reload_doc("setup", "doctype", "quotation_lost_reason_detail", force=True)

	company = vmraid.get_all("Company", filters={"country": "United States"})
	if not company:
		return

	make_custom_fields()
