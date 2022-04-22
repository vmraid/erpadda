# Copyright (c) 2018, VMRaid and Contributors
# See license.txt

import unittest

import vmraid


class TestCourseActivity(unittest.TestCase):
	pass


def make_course_activity(enrollment, content_type, content):
	activity = vmraid.get_all(
		"Course Activity",
		filters={"enrollment": enrollment, "content_type": content_type, "content": content},
	)
	try:
		activity = vmraid.get_doc("Course Activity", activity[0]["name"])
	except (IndexError, vmraid.DoesNotExistError):
		activity = vmraid.get_doc(
			{
				"doctype": "Course Activity",
				"enrollment": enrollment,
				"content_type": content_type,
				"content": content,
				"activity_date": vmraid.utils.datetime.datetime.now(),
			}
		).insert()
	return activity
