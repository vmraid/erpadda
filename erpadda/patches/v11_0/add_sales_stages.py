import vmraid

from erpadda.setup.setup_wizard.operations.install_fixtures import add_sale_stages


def execute():
	vmraid.reload_doc("crm", "doctype", "sales_stage")

	vmraid.local.lang = vmraid.db.get_default("lang") or "en"

	add_sale_stages()
