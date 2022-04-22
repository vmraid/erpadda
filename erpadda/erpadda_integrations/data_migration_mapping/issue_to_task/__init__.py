import vmraid


def pre_process(issue):

	project = vmraid.db.get_value("Project", filters={"project_name": issue.milestone})
	return {
		"title": issue.title,
		"body": vmraid.utils.md_to_html(issue.body or ""),
		"state": issue.state.title(),
		"project": project or "",
	}
