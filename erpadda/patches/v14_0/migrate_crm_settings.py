import vmraid


def execute():
	settings = vmraid.db.get_value(
		"Selling Settings",
		"Selling Settings",
		["campaign_naming_by", "close_opportunity_after_days", "default_valid_till"],
		as_dict=True,
	)

	vmraid.reload_doc("crm", "doctype", "crm_settings")
	if settings:
		vmraid.db.set_value(
			"CRM Settings",
			"CRM Settings",
			{
				"campaign_naming_by": settings.campaign_naming_by,
				"close_opportunity_after_days": settings.close_opportunity_after_days,
				"default_valid_till": settings.default_valid_till,
			},
		)
