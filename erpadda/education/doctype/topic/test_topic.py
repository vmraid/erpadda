# Copyright (c) 2018, VMRaid and Contributors
# See license.txt

import unittest

import vmraid


class TestTopic(unittest.TestCase):
	def setUp(self):
		make_topic_and_linked_content("_Test Topic 1", [{"type": "Article", "name": "_Test Article 1"}])

	def test_get_contents(self):
		topic = vmraid.get_doc("Topic", "_Test Topic 1")
		contents = topic.get_contents()
		self.assertEqual(contents[0].doctype, "Article")
		self.assertEqual(contents[0].name, "_Test Article 1")
		vmraid.db.rollback()


def make_topic(name):
	try:
		topic = vmraid.get_doc("Topic", name)
	except vmraid.DoesNotExistError:
		topic = vmraid.get_doc(
			{
				"doctype": "Topic",
				"topic_name": name,
				"topic_code": name,
			}
		).insert()
	return topic.name


def make_topic_and_linked_content(topic_name, content_dict_list):
	try:
		topic = vmraid.get_doc("Topic", topic_name)
	except vmraid.DoesNotExistError:
		make_topic(topic_name)
		topic = vmraid.get_doc("Topic", topic_name)
	content_list = [make_content(content["type"], content["name"]) for content in content_dict_list]
	for content in content_list:
		topic.append("topic_content", {"content": content.title, "content_type": content.doctype})
	topic.save()
	return topic


def make_content(type, name):
	try:
		content = vmraid.get_doc(type, name)
	except vmraid.DoesNotExistError:
		content = vmraid.get_doc({"doctype": type, "title": name}).insert()
	return content
