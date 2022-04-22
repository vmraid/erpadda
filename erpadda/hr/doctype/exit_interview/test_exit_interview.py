# Copyright (c) 2021, VMRaid and Contributors
# See license.txt

import os
import unittest

import vmraid
from vmraid import _
from vmraid.core.doctype.user_permission.test_user_permission import create_user
from vmraid.tests.test_webform import create_custom_doctype, create_webform
from vmraid.utils import getdate

from erpadda.hr.doctype.employee.test_employee import make_employee
from erpadda.hr.doctype.exit_interview.exit_interview import send_exit_questionnaire


class TestExitInterview(unittest.TestCase):
	def setUp(self):
		vmraid.db.sql("delete from `tabExit Interview`")

	def test_duplicate_interview(self):
		employee = make_employee("employeeexitint1@example.com")
		vmraid.db.set_value("Employee", employee, "relieving_date", getdate())
		interview = create_exit_interview(employee)

		doc = vmraid.copy_doc(interview)
		self.assertRaises(vmraid.DuplicateEntryError, doc.save)

	def test_relieving_date_validation(self):
		employee = make_employee("employeeexitint2@example.com")
		# unset relieving date
		vmraid.db.set_value("Employee", employee, "relieving_date", None)

		interview = create_exit_interview(employee, save=False)
		self.assertRaises(vmraid.ValidationError, interview.save)

		# set relieving date
		vmraid.db.set_value("Employee", employee, "relieving_date", getdate())
		interview = create_exit_interview(employee)
		self.assertTrue(interview.name)

	def test_interview_date_updated_in_employee_master(self):
		employee = make_employee("employeeexit3@example.com")
		vmraid.db.set_value("Employee", employee, "relieving_date", getdate())

		interview = create_exit_interview(employee)
		interview.status = "Completed"
		interview.employee_status = "Exit Confirmed"

		# exit interview date updated on submit
		interview.submit()
		self.assertEqual(vmraid.db.get_value("Employee", employee, "held_on"), interview.date)

		# exit interview reset on cancel
		interview.reload()
		interview.cancel()
		self.assertEqual(vmraid.db.get_value("Employee", employee, "held_on"), None)

	def test_send_exit_questionnaire(self):
		create_custom_doctype()
		create_webform()
		template = create_notification_template()

		webform = vmraid.db.get_all("Web Form", limit=1)
		vmraid.db.set_value(
			"HR Settings",
			"HR Settings",
			{
				"exit_questionnaire_web_form": webform[0].name,
				"exit_questionnaire_notification_template": template,
			},
		)

		employee = make_employee("employeeexit3@example.com")
		vmraid.db.set_value("Employee", employee, "relieving_date", getdate())

		interview = create_exit_interview(employee)
		send_exit_questionnaire([interview])

		email_queue = vmraid.db.get_all("Email Queue", ["name", "message"], limit=1)
		self.assertTrue("Subject: Exit Questionnaire Notification" in email_queue[0].message)

	def tearDown(self):
		vmraid.db.rollback()


def create_exit_interview(employee, save=True):
	interviewer = create_user("test_exit_interviewer@example.com")

	doc = vmraid.get_doc(
		{
			"doctype": "Exit Interview",
			"employee": employee,
			"company": "_Test Company",
			"status": "Pending",
			"date": getdate(),
			"interviewers": [{"interviewer": interviewer.name}],
			"interview_summary": "Test",
		}
	)

	if save:
		return doc.insert()
	return doc


def create_notification_template():
	template = vmraid.db.exists("Email Template", _("Exit Questionnaire Notification"))
	if not template:
		base_path = vmraid.get_app_path("erpadda", "hr", "doctype")
		response = vmraid.read_file(
			os.path.join(base_path, "exit_interview/exit_questionnaire_notification_template.html")
		)

		template = vmraid.get_doc(
			{
				"doctype": "Email Template",
				"name": _("Exit Questionnaire Notification"),
				"response": response,
				"subject": _("Exit Questionnaire Notification"),
				"owner": vmraid.session.user,
			}
		).insert(ignore_permissions=True)
		template = template.name

	return template
