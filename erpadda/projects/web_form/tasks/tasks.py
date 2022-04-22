import vmraid


def get_context(context):
	if vmraid.form_dict.project:
		context.parents = [
			{"title": vmraid.form_dict.project, "route": "/projects?project=" + vmraid.form_dict.project}
		]
		context.success_url = "/projects?project=" + vmraid.form_dict.project

	elif context.doc and context.doc.get("project"):
		context.parents = [
			{"title": context.doc.project, "route": "/projects?project=" + context.doc.project}
		]
		context.success_url = "/projects?project=" + context.doc.project
