import vmraid


def get_context(context):
	context.no_cache = 1

	timelog = vmraid.get_doc("Time Log", vmraid.form_dict.timelog)

	context.doc = timelog
