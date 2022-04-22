import vmraid
from vmraid.model.utils.rename_field import rename_field


def execute():
	vmraid.reload_doc("automation", "doctype", "auto_repeat")

	doctypes_to_rename = {
		"accounts": ["Journal Entry", "Payment Entry", "Purchase Invoice", "Sales Invoice"],
		"buying": ["Purchase Order", "Supplier Quotation"],
		"selling": ["Quotation", "Sales Order"],
		"stock": ["Delivery Note", "Purchase Receipt"],
	}

	for module, doctypes in doctypes_to_rename.items():
		for doctype in doctypes:
			vmraid.reload_doc(module, "doctype", vmraid.scrub(doctype))

			if vmraid.db.has_column(doctype, "subscription"):
				rename_field(doctype, "subscription", "auto_repeat")

	subscriptions = vmraid.db.sql("select * from `tabSubscription`", as_dict=1)

	for doc in subscriptions:
		doc["doctype"] = "Auto Repeat"
		auto_repeat = vmraid.get_doc(doc)
		auto_repeat.db_insert()

	vmraid.db.sql("delete from `tabSubscription`")
	vmraid.db.commit()
	drop_columns_from_subscription()


def drop_columns_from_subscription():
	fields_to_drop = {"Subscription": []}
	for field in [
		"naming_series",
		"reference_doctype",
		"reference_document",
		"start_date",
		"end_date",
		"submit_on_creation",
		"disabled",
		"frequency",
		"repeat_on_day",
		"next_schedule_date",
		"notify_by_email",
		"subject",
		"recipients",
		"print_format",
		"message",
		"status",
		"amended_from",
	]:

		if field in vmraid.db.get_table_columns("Subscription"):
			fields_to_drop["Subscription"].append(field)

	vmraid.model.delete_fields(fields_to_drop, delete=1)
