# Copyright (c) 2015, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


from erpadda.accounts.report.accounts_receivable_summary.accounts_receivable_summary import (
	AccountsReceivableSummary,
)


def execute(filters=None):
	args = {
		"party_type": "Supplier",
		"naming_by": ["Buying Settings", "supp_master_name"],
	}
	return AccountsReceivableSummary(filters).run(args)
