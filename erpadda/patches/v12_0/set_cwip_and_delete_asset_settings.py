import vmraid
from vmraid.utils import cint


def execute():
	"""Get 'Disable CWIP Accounting value' from Asset Settings, set it in 'Enable Capital Work in Progress Accounting' field
	in Company, delete Asset Settings"""

	if vmraid.db.exists("DocType", "Asset Settings"):
		vmraid.reload_doctype("Asset Category")
		cwip_value = vmraid.db.get_single_value("Asset Settings", "disable_cwip_accounting")

		vmraid.db.sql("""UPDATE `tabAsset Category` SET enable_cwip_accounting = %s""", cint(cwip_value))

		vmraid.db.sql("""DELETE FROM `tabSingles` where doctype = 'Asset Settings'""")
		vmraid.delete_doc_if_exists("DocType", "Asset Settings")
