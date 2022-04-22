import vmraid


def execute():
	vmraid.reload_doc("core", "doctype", "scheduled_job_type")
	if vmraid.db.exists("Scheduled Job Type", "repost_item_valuation.repost_entries"):
		vmraid.db.set_value("Scheduled Job Type", "repost_item_valuation.repost_entries", "stopped", 0)
