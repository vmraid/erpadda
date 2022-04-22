import vmraid


def get_context(context):
	context.no_cache = 1

	task = vmraid.get_doc("Task", vmraid.form_dict.task)

	context.comments = vmraid.get_all(
		"Communication",
		filters={"reference_name": task.name, "comment_type": "comment"},
		fields=["subject", "sender_full_name", "communication_date"],
	)

	context.doc = task
