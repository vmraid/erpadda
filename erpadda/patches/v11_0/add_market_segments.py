import vmraid

from erpadda.setup.setup_wizard.operations.install_fixtures import add_market_segments


def execute():
	vmraid.reload_doc("crm", "doctype", "market_segment")

	vmraid.local.lang = vmraid.db.get_default("lang") or "en"

	add_market_segments()
