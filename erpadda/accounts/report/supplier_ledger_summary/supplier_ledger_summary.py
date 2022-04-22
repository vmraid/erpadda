# Copyright (c) 2013, VMRaid and contributors
# For license information, please see license.txt


from erpadda.accounts.report.customer_ledger_summary.customer_ledger_summary import (
	PartyLedgerSummaryReport,
)


def execute(filters=None):
	args = {
		"party_type": "Supplier",
		"naming_by": ["Buying Settings", "supp_master_name"],
	}
	return PartyLedgerSummaryReport(filters).run(args)
