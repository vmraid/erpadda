# Copyright (c) 2018, VMRaid and contributors
# For license information, please see license.txt


import json

import vmraid
from vmraid import _
from vmraid.model.document import Document


class Topic(Document):
	def get_contents(self):
		try:
			topic_content_list = self.topic_content
			content_data = [
				vmraid.get_doc(topic_content.content_type, topic_content.content)
				for topic_content in topic_content_list
			]
		except Exception as e:
			vmraid.log_error(vmraid.get_traceback())
			return None
		return content_data


@vmraid.whitelist()
def get_courses_without_topic(topic):
	data = []
	for entry in vmraid.db.get_all("Course"):
		course = vmraid.get_doc("Course", entry.name)
		topics = [t.topic for t in course.topics]
		if not topics or topic not in topics:
			data.append(course.name)
	return data


@vmraid.whitelist()
def add_topic_to_courses(topic, courses, mandatory=False):
	courses = json.loads(courses)
	for entry in courses:
		course = vmraid.get_doc("Course", entry)
		course.append("topics", {"topic": topic, "topic_name": topic})
		course.flags.ignore_mandatory = True
		course.save()
	vmraid.db.commit()
	vmraid.msgprint(
		_("Topic {0} has been added to all the selected courses successfully.").format(
			vmraid.bold(topic)
		),
		title=_("Courses updated"),
		indicator="green",
	)


@vmraid.whitelist()
def add_content_to_topics(content_type, content, topics):
	topics = json.loads(topics)
	for entry in topics:
		topic = vmraid.get_doc("Topic", entry)
		topic.append(
			"topic_content",
			{
				"content_type": content_type,
				"content": content,
			},
		)
		topic.flags.ignore_mandatory = True
		topic.save()
	vmraid.db.commit()
	vmraid.msgprint(
		_("{0} {1} has been added to all the selected topics successfully.").format(
			content_type, vmraid.bold(content)
		),
		title=_("Topics updated"),
		indicator="green",
	)
