# Copyright (c) 2019, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid


def execute():

	if vmraid.db.exists("DocType", "Bank Reconciliation Detail") and vmraid.db.exists(
		"DocType", "Bank Clearance Detail"
	):

		vmraid.delete_doc("DocType", "Bank Reconciliation Detail", force=1)
