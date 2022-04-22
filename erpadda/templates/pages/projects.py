# Copyright (c) 2015, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid


def get_context(context):
	project_user = vmraid.db.get_value(
		"Project User",
		{"parent": vmraid.form_dict.project, "user": vmraid.session.user},
		["user", "view_attachments"],
		as_dict=True,
	)
	if vmraid.session.user != "Administrator" and (
		not project_user or vmraid.session.user == "Guest"
	):
		raise vmraid.PermissionError

	context.no_cache = 1
	context.show_sidebar = True
	project = vmraid.get_doc("Project", vmraid.form_dict.project)

	project.has_permission("read")

	project.tasks = get_tasks(
		project.name, start=0, item_status="open", search=vmraid.form_dict.get("search")
	)

	project.timesheets = get_timesheets(project.name, start=0, search=vmraid.form_dict.get("search"))

	if project_user and project_user.view_attachments:
		project.attachments = get_attachments(project.name)

	context.doc = project


def get_tasks(project, start=0, search=None, item_status=None):
	filters = {"project": project}
	if search:
		filters["subject"] = ("like", "%{0}%".format(search))
	tasks = vmraid.get_all(
		"Task",
		filters=filters,
		fields=[
			"name",
			"subject",
			"status",
			"modified",
			"_assign",
			"exp_end_date",
			"is_group",
			"parent_task",
		],
		limit_start=start,
		limit_page_length=10,
	)
	task_nest = []
	for task in tasks:
		if task.is_group:
			child_tasks = list(filter(lambda x: x.parent_task == task.name, tasks))
			if len(child_tasks):
				task.children = child_tasks
		task_nest.append(task)
	return list(filter(lambda x: not x.parent_task, tasks))


@vmraid.whitelist()
def get_task_html(project, start=0, item_status=None):
	return vmraid.render_template(
		"erpadda/templates/includes/projects/project_tasks.html",
		{
			"doc": {
				"name": project,
				"project_name": project,
				"tasks": get_tasks(project, start, item_status=item_status),
			}
		},
		is_path=True,
	)


def get_timesheets(project, start=0, search=None):
	filters = {"project": project}
	if search:
		filters["activity_type"] = ("like", "%{0}%".format(search))

	timesheets = vmraid.get_all(
		"Timesheet Detail",
		filters=filters,
		fields=["project", "activity_type", "from_time", "to_time", "parent"],
		limit_start=start,
		limit_page_length=10,
	)
	for timesheet in timesheets:
		info = vmraid.get_all(
			"Timesheet",
			filters={"name": timesheet.parent},
			fields=["name", "status", "modified", "modified_by"],
			limit_start=start,
			limit_page_length=10,
		)
		if len(info):
			timesheet.update(info[0])
	return timesheets


@vmraid.whitelist()
def get_timesheet_html(project, start=0):
	return vmraid.render_template(
		"erpadda/templates/includes/projects/project_timesheets.html",
		{"doc": {"timesheets": get_timesheets(project, start)}},
		is_path=True,
	)


def get_attachments(project):
	return vmraid.get_all(
		"File",
		filters={"attached_to_name": project, "attached_to_doctype": "Project", "is_private": 0},
		fields=["file_name", "file_url", "file_size"],
	)
