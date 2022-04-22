import vmraid


def execute():
	active_sla_documents = [
		sla.document_type for sla in vmraid.get_all("Service Level Agreement", fields=["document_type"])
	]

	for doctype in active_sla_documents:
		doctype = vmraid.qb.DocType(doctype)
		try:
			vmraid.qb.update(doctype).set(doctype.agreement_status, "First Response Due").where(
				doctype.first_responded_on.isnull()
			).run()

			vmraid.qb.update(doctype).set(doctype.agreement_status, "Resolution Due").where(
				doctype.agreement_status == "Ongoing"
			).run()

		except Exception:
			vmraid.log_error(title="Failed to Patch SLA Status")
