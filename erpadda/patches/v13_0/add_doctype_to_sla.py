# Copyright (c) 2020, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid
from vmraid.model.utils.rename_field import rename_field


def execute():
	vmraid.reload_doc("support", "doctype", "sla_fulfilled_on_status")
	vmraid.reload_doc("support", "doctype", "service_level_agreement")
	if vmraid.db.has_column("Service Level Agreement", "enable"):
		rename_field("Service Level Agreement", "enable", "enabled")

	for sla in vmraid.get_all("Service Level Agreement"):
		agreement = vmraid.get_doc("Service Level Agreement", sla.name)
		agreement.document_type = "Issue"
		agreement.apply_sla_for_resolution = 1
		agreement.append("sla_fulfilled_on", {"status": "Resolved"})
		agreement.append("sla_fulfilled_on", {"status": "Closed"})
		agreement.save()
