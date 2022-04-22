# Copyright (c) 2019, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt

import vmraid


def execute():
	accounts_settings = vmraid.get_doc("Accounts Settings", "Accounts Settings")
	accounts_settings.book_deferred_entries_based_on = "Days"
	accounts_settings.book_deferred_entries_via_journal_entry = 0
	accounts_settings.submit_journal_entries = 0
	accounts_settings.save()
