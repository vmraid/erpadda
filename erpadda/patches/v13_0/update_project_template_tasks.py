# Copyright (c) 2019, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid


def execute():
	vmraid.reload_doc("projects", "doctype", "project_template")
	vmraid.reload_doc("projects", "doctype", "project_template_task")
	vmraid.reload_doc("projects", "doctype", "task")

	# Update property setter status if any
	property_setter = vmraid.db.get_value(
		"Property Setter", {"doc_type": "Task", "field_name": "status", "property": "options"}
	)

	if property_setter:
		property_setter_doc = vmraid.get_doc(
			"Property Setter", {"doc_type": "Task", "field_name": "status", "property": "options"}
		)
		property_setter_doc.value += "\nTemplate"
		property_setter_doc.save()

	for template_name in vmraid.get_all("Project Template"):
		template = vmraid.get_doc("Project Template", template_name.name)
		replace_tasks = False
		new_tasks = []
		for task in template.tasks:
			if task.subject:
				replace_tasks = True
				new_task = vmraid.get_doc(
					dict(
						doctype="Task",
						subject=task.subject,
						start=task.start,
						duration=task.duration,
						task_weight=task.task_weight,
						description=task.description,
						is_template=1,
					)
				).insert()
				new_tasks.append(new_task)

		if replace_tasks:
			template.tasks = []
			for tsk in new_tasks:
				template.append("tasks", {"task": tsk.name, "subject": tsk.subject})
			template.save()
