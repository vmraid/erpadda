# Copyright (c) 2017, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid


def execute():
	vmraid.reload_doc("setup", "doctype", "target_detail")
	vmraid.reload_doc("core", "doctype", "prepared_report")

	for d in ["Sales Person", "Sales Partner", "Territory"]:
		vmraid.db.sql(
			"""
            UPDATE `tab{child_doc}`, `tab{parent_doc}`
            SET
                `tab{child_doc}`.distribution_id = `tab{parent_doc}`.distribution_id
            WHERE
                `tab{child_doc}`.parent = `tab{parent_doc}`.name
                and `tab{parent_doc}`.distribution_id is not null and `tab{parent_doc}`.distribution_id != ''
        """.format(
				parent_doc=d, child_doc="Target Detail"
			)
		)

	vmraid.delete_doc("Report", "Sales Partner-wise Transaction Summary")
	vmraid.delete_doc("Report", "Sales Person Target Variance Item Group-Wise")
	vmraid.delete_doc("Report", "Territory Target Variance Item Group-Wise")
