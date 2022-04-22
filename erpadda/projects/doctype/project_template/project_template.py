# Copyright (c) 2019, VMRaid and contributors
# For license information, please see license.txt


import vmraid
from vmraid import _
from vmraid.model.document import Document
from vmraid.utils import get_link_to_form


class ProjectTemplate(Document):
	def validate(self):
		self.validate_dependencies()

	def validate_dependencies(self):
		for task in self.tasks:
			task_details = vmraid.get_doc("Task", task.task)
			if task_details.depends_on:
				for dependency_task in task_details.depends_on:
					if not self.check_dependent_task_presence(dependency_task.task):
						task_details_format = get_link_to_form("Task", task_details.name)
						dependency_task_format = get_link_to_form("Task", dependency_task.task)
						vmraid.throw(
							_("Task {0} depends on Task {1}. Please add Task {1} to the Tasks list.").format(
								vmraid.bold(task_details_format), vmraid.bold(dependency_task_format)
							)
						)

	def check_dependent_task_presence(self, task):
		for task_details in self.tasks:
			if task_details.task == task:
				return True
		return False
