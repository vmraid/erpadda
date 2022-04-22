# Copyright (c) 2015, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt"


import vmraid
from vmraid.utils import cint


def boot_session(bootinfo):
	"""boot session - send website info if guest"""

	bootinfo.custom_css = vmraid.db.get_value("Style Settings", None, "custom_css") or ""

	if vmraid.session["user"] != "Guest":
		update_page_info(bootinfo)

		load_country_and_currency(bootinfo)
		bootinfo.sysdefaults.territory = vmraid.db.get_single_value("Selling Settings", "territory")
		bootinfo.sysdefaults.customer_group = vmraid.db.get_single_value(
			"Selling Settings", "customer_group"
		)
		bootinfo.sysdefaults.allow_stale = cint(
			vmraid.db.get_single_value("Accounts Settings", "allow_stale")
		)
		bootinfo.sysdefaults.quotation_valid_till = cint(
			vmraid.db.get_single_value("CRM Settings", "default_valid_till")
		)

		# if no company, show a dialog box to create a new company
		bootinfo.customer_count = vmraid.db.sql("""SELECT count(*) FROM `tabCustomer`""")[0][0]

		if not bootinfo.customer_count:
			bootinfo.setup_complete = (
				vmraid.db.sql(
					"""SELECT `name`
				FROM `tabCompany`
				LIMIT 1"""
				)
				and "Yes"
				or "No"
			)

		bootinfo.docs += vmraid.db.sql(
			"""select name, default_currency, cost_center, default_selling_terms, default_buying_terms,
			default_letter_head, default_bank_account, enable_perpetual_inventory, country from `tabCompany`""",
			as_dict=1,
			update={"doctype": ":Company"},
		)

		party_account_types = vmraid.db.sql(
			""" select name, ifnull(account_type, '') from `tabParty Type`"""
		)
		bootinfo.party_account_types = vmraid._dict(party_account_types)


def load_country_and_currency(bootinfo):
	country = vmraid.db.get_default("country")
	if country and vmraid.db.exists("Country", country):
		bootinfo.docs += [vmraid.get_doc("Country", country)]

	bootinfo.docs += vmraid.db.sql(
		"""select name, fraction, fraction_units,
		number_format, smallest_currency_fraction_value, symbol from tabCurrency
		where enabled=1""",
		as_dict=1,
		update={"doctype": ":Currency"},
	)


def update_page_info(bootinfo):
	bootinfo.page_info.update(
		{
			"Chart of Accounts": {"title": "Chart of Accounts", "route": "Tree/Account"},
			"Chart of Cost Centers": {"title": "Chart of Cost Centers", "route": "Tree/Cost Center"},
			"Item Group Tree": {"title": "Item Group Tree", "route": "Tree/Item Group"},
			"Customer Group Tree": {"title": "Customer Group Tree", "route": "Tree/Customer Group"},
			"Territory Tree": {"title": "Territory Tree", "route": "Tree/Territory"},
			"Sales Person Tree": {"title": "Sales Person Tree", "route": "Tree/Sales Person"},
		}
	)
