import vmraid
from vmraid.utils import cint


def execute():
	vmraid.reload_doc("erpadda_integrations", "doctype", "woocommerce_settings")
	doc = vmraid.get_doc("Woocommerce Settings")

	if cint(doc.enable_sync):
		doc.creation_user = doc.modified_by
		doc.save(ignore_permissions=True)
