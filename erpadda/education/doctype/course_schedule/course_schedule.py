# -*- coding: utf-8 -*-
# Copyright (c) 2015, VMRaid Technologies and contributors
# For license information, please see license.txt


from datetime import datetime

import vmraid
from vmraid import _
from vmraid.model.document import Document


class CourseSchedule(Document):
	def validate(self):
		self.instructor_name = vmraid.db.get_value("Instructor", self.instructor, "instructor_name")
		self.set_title()
		self.validate_course()
		self.validate_date()
		self.validate_overlap()

	def set_title(self):
		"""Set document Title"""
		self.title = (
			self.course + " by " + (self.instructor_name if self.instructor_name else self.instructor)
		)

	def validate_course(self):
		group_based_on, course = vmraid.db.get_value(
			"Student Group", self.student_group, ["group_based_on", "course"]
		)
		if group_based_on == "Course":
			self.course = course

	def validate_date(self):
		"""Validates if from_time is greater than to_time"""
		if self.from_time > self.to_time:
			vmraid.throw(_("From Time cannot be greater than To Time."))

		"""Handles specicfic case to update schedule date in calendar """
		if isinstance(self.from_time, str):
			try:
				datetime_obj = datetime.strptime(self.from_time, "%Y-%m-%d %H:%M:%S")
				self.schedule_date = datetime_obj
			except ValueError:
				pass

	def validate_overlap(self):
		"""Validates overlap for Student Group, Instructor, Room"""

		from erpadda.education.utils import validate_overlap_for

		# Validate overlapping course schedules.
		if self.student_group:
			validate_overlap_for(self, "Course Schedule", "student_group")

		validate_overlap_for(self, "Course Schedule", "instructor")
		validate_overlap_for(self, "Course Schedule", "room")

		# validate overlapping assessment schedules.
		if self.student_group:
			validate_overlap_for(self, "Assessment Plan", "student_group")

		validate_overlap_for(self, "Assessment Plan", "room")
		validate_overlap_for(self, "Assessment Plan", "supervisor", self.instructor)
