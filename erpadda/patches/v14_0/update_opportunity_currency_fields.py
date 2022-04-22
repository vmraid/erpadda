import vmraid
from vmraid.utils import flt

import erpadda
from erpadda.setup.utils import get_exchange_rate


def execute():
	vmraid.reload_doctype("Opportunity")
	opportunities = vmraid.db.get_list(
		"Opportunity",
		filters={"opportunity_amount": [">", 0]},
		fields=["name", "company", "currency", "opportunity_amount"],
	)

	for opportunity in opportunities:
		company_currency = erpadda.get_company_currency(opportunity.company)

		# base total and total will be 0 only since item table did not have amount field earlier
		if opportunity.currency != company_currency:
			conversion_rate = get_exchange_rate(opportunity.currency, company_currency)
			base_opportunity_amount = flt(conversion_rate) * flt(opportunity.opportunity_amount)
		else:
			conversion_rate = 1
			base_opportunity_amount = flt(opportunity.opportunity_amount)

		vmraid.db.set_value(
			"Opportunity",
			opportunity.name,
			{"conversion_rate": conversion_rate, "base_opportunity_amount": base_opportunity_amount},
			update_modified=False,
		)
