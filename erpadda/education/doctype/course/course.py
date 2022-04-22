# Copyright (c) 2015, VMRaid Technologies and contributors
# For license information, please see license.txt


import json

import vmraid
from vmraid import _
from vmraid.model.document import Document


class Course(Document):
	def validate(self):
		self.validate_assessment_criteria()

	def validate_assessment_criteria(self):
		if self.assessment_criteria:
			total_weightage = 0
			for criteria in self.assessment_criteria:
				total_weightage += criteria.weightage or 0
			if total_weightage != 100:
				vmraid.throw(_("Total Weightage of all Assessment Criteria must be 100%"))

	def get_topics(self):
		topic_data = []
		for topic in self.topics:
			topic_doc = vmraid.get_doc("Topic", topic.topic)
			if topic_doc.topic_content:
				topic_data.append(topic_doc)
		return topic_data


@vmraid.whitelist()
def add_course_to_programs(course, programs, mandatory=False):
	programs = json.loads(programs)
	for entry in programs:
		program = vmraid.get_doc("Program", entry)
		program.append("courses", {"course": course, "course_name": course, "mandatory": mandatory})
		program.flags.ignore_mandatory = True
		program.save()
	vmraid.db.commit()
	vmraid.msgprint(
		_("Course {0} has been added to all the selected programs successfully.").format(
			vmraid.bold(course)
		),
		title=_("Programs updated"),
		indicator="green",
	)


@vmraid.whitelist()
def get_programs_without_course(course):
	data = []
	for entry in vmraid.db.get_all("Program"):
		program = vmraid.get_doc("Program", entry.name)
		courses = [c.course for c in program.courses]
		if not courses or course not in courses:
			data.append(program.name)
	return data
