# Copyright (c) 2015, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid


def execute():
	vmraid.reload_doctype("Quotation")
	vmraid.db.sql(""" UPDATE `tabQuotation` set party_name = lead WHERE quotation_to = 'Lead' """)
	vmraid.db.sql(
		""" UPDATE `tabQuotation` set party_name = customer WHERE quotation_to = 'Customer' """
	)

	vmraid.reload_doctype("Opportunity")
	vmraid.db.sql(
		""" UPDATE `tabOpportunity` set party_name = lead WHERE opportunity_from = 'Lead' """
	)
	vmraid.db.sql(
		""" UPDATE `tabOpportunity` set party_name = customer WHERE opportunity_from = 'Customer' """
	)
