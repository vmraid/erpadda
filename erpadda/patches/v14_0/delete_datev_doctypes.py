import vmraid


def execute():
	install_apps = vmraid.get_installed_apps()
	if "erpadda_datev_uo" in install_apps or "erpadda_datev" in install_apps:
		return

	# doctypes
	vmraid.delete_doc("DocType", "DATEV Settings", ignore_missing=True, force=True)

	# reports
	vmraid.delete_doc("Report", "DATEV", ignore_missing=True, force=True)
