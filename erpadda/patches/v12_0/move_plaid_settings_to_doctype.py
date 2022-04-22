# Copyright (c) 2017, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid


def execute():
	vmraid.reload_doc("erpadda_integrations", "doctype", "plaid_settings")
	plaid_settings = vmraid.get_single("Plaid Settings")
	if plaid_settings.enabled:
		if not (vmraid.conf.plaid_client_id and vmraid.conf.plaid_env and vmraid.conf.plaid_secret):
			plaid_settings.enabled = 0
		else:
			plaid_settings.update(
				{
					"plaid_client_id": vmraid.conf.plaid_client_id,
					"plaid_env": vmraid.conf.plaid_env,
					"plaid_secret": vmraid.conf.plaid_secret,
				}
			)
		plaid_settings.flags.ignore_mandatory = True
		plaid_settings.save()
