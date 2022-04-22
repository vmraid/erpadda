import inspect

import vmraid

__version__ = "14.0.0-dev"


def get_default_company(user=None):
	"""Get default company for user"""
	from vmraid.defaults import get_user_default_as_list

	if not user:
		user = vmraid.session.user

	companies = get_user_default_as_list(user, "company")
	if companies:
		default_company = companies[0]
	else:
		default_company = vmraid.db.get_single_value("Global Defaults", "default_company")

	return default_company


def get_default_currency():
	"""Returns the currency of the default company"""
	company = get_default_company()
	if company:
		return vmraid.get_cached_value("Company", company, "default_currency")


def get_default_cost_center(company):
	"""Returns the default cost center of the company"""
	if not company:
		return None

	if not vmraid.flags.company_cost_center:
		vmraid.flags.company_cost_center = {}
	if not company in vmraid.flags.company_cost_center:
		vmraid.flags.company_cost_center[company] = vmraid.get_cached_value(
			"Company", company, "cost_center"
		)
	return vmraid.flags.company_cost_center[company]


def get_company_currency(company):
	"""Returns the default company currency"""
	if not vmraid.flags.company_currency:
		vmraid.flags.company_currency = {}
	if not company in vmraid.flags.company_currency:
		vmraid.flags.company_currency[company] = vmraid.db.get_value(
			"Company", company, "default_currency", cache=True
		)
	return vmraid.flags.company_currency[company]


def set_perpetual_inventory(enable=1, company=None):
	if not company:
		company = "_Test Company" if vmraid.flags.in_test else get_default_company()

	company = vmraid.get_doc("Company", company)
	company.enable_perpetual_inventory = enable
	company.save()


def encode_company_abbr(name, company=None, abbr=None):
	"""Returns name encoded with company abbreviation"""
	company_abbr = abbr or vmraid.get_cached_value("Company", company, "abbr")
	parts = name.rsplit(" - ", 1)

	if parts[-1].lower() != company_abbr.lower():
		parts.append(company_abbr)

	return " - ".join(parts)


def is_perpetual_inventory_enabled(company):
	if not company:
		company = "_Test Company" if vmraid.flags.in_test else get_default_company()

	if not hasattr(vmraid.local, "enable_perpetual_inventory"):
		vmraid.local.enable_perpetual_inventory = {}

	if not company in vmraid.local.enable_perpetual_inventory:
		vmraid.local.enable_perpetual_inventory[company] = (
			vmraid.get_cached_value("Company", company, "enable_perpetual_inventory") or 0
		)

	return vmraid.local.enable_perpetual_inventory[company]


def get_default_finance_book(company=None):
	if not company:
		company = get_default_company()

	if not hasattr(vmraid.local, "default_finance_book"):
		vmraid.local.default_finance_book = {}

	if not company in vmraid.local.default_finance_book:
		vmraid.local.default_finance_book[company] = vmraid.get_cached_value(
			"Company", company, "default_finance_book"
		)

	return vmraid.local.default_finance_book[company]


def get_party_account_type(party_type):
	if not hasattr(vmraid.local, "party_account_types"):
		vmraid.local.party_account_types = {}

	if not party_type in vmraid.local.party_account_types:
		vmraid.local.party_account_types[party_type] = (
			vmraid.db.get_value("Party Type", party_type, "account_type") or ""
		)

	return vmraid.local.party_account_types[party_type]


def get_region(company=None):
	"""Return the default country based on flag, company or global settings

	You can also set global company flag in `vmraid.flags.company`
	"""
	if company or vmraid.flags.company:
		return vmraid.get_cached_value("Company", company or vmraid.flags.company, "country")
	elif vmraid.flags.country:
		return vmraid.flags.country
	else:
		return vmraid.get_system_settings("country")


def allow_regional(fn):
	"""Decorator to make a function regionally overridable

	Example:
	@erpadda.allow_regional
	def myfunction():
	  pass"""

	def caller(*args, **kwargs):
		overrides = vmraid.get_hooks("regional_overrides", {}).get(get_region())
		function_path = f"{inspect.getmodule(fn).__name__}.{fn.__name__}"

		if not overrides or function_path not in overrides:
			return fn(*args, **kwargs)

		# Priority given to last installed app
		return vmraid.get_attr(overrides[function_path][-1])(*args, **kwargs)

	return caller
