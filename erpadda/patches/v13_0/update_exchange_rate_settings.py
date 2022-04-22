import vmraid

from erpadda.setup.install import setup_currency_exchange


def execute():
	vmraid.reload_doc("accounts", "doctype", "currency_exchange_settings_result")
	vmraid.reload_doc("accounts", "doctype", "currency_exchange_settings_details")
	vmraid.reload_doc("accounts", "doctype", "currency_exchange_settings")
	setup_currency_exchange()
