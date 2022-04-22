import vmraid


def execute():
	if vmraid.db.table_exists("Offer Letter") and not vmraid.db.table_exists("Job Offer"):
		vmraid.rename_doc("DocType", "Offer Letter", "Job Offer", force=True)
		vmraid.rename_doc("DocType", "Offer Letter Term", "Job Offer Term", force=True)
		vmraid.reload_doc("hr", "doctype", "job_offer")
		vmraid.reload_doc("hr", "doctype", "job_offer_term")
		vmraid.delete_doc("Print Format", "Offer Letter")
