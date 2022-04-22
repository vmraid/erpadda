# Copyright (c) 2017, VMRaid and contributors
# For license information, please see license.txt


import vmraid
from vmraid import _
from vmraid.model.document import Document
from vmraid.model.mapper import get_mapped_doc
from vmraid.utils import cint, cstr, flt, money_in_words
from vmraid.utils.background_jobs import enqueue

import erpadda


class FeeSchedule(Document):
	def onload(self):
		info = self.get_dashboard_info()
		self.set_onload("dashboard_info", info)

	def get_dashboard_info(self):
		info = {
			"total_paid": 0,
			"total_unpaid": 0,
			"currency": erpadda.get_company_currency(self.company),
		}

		fees_amount = vmraid.db.sql(
			"""select sum(grand_total), sum(outstanding_amount) from tabFees
			where fee_schedule=%s and docstatus=1""",
			(self.name),
		)

		if fees_amount:
			info["total_paid"] = flt(fees_amount[0][0]) - flt(fees_amount[0][1])
			info["total_unpaid"] = flt(fees_amount[0][1])

		return info

	def validate(self):
		self.calculate_total_and_program()

	def calculate_total_and_program(self):
		no_of_students = 0
		for d in self.student_groups:
			# if not d.total_students:
			d.total_students = get_total_students(
				d.student_group, self.academic_year, self.academic_term, self.student_category
			)
			no_of_students += cint(d.total_students)

			# validate the program of fee structure and student groups
			student_group_program = vmraid.db.get_value("Student Group", d.student_group, "program")
			if self.program and student_group_program and self.program != student_group_program:
				vmraid.msgprint(
					_("Program in the Fee Structure and Student Group {0} are different.").format(d.student_group)
				)
		self.grand_total = no_of_students * self.total_amount
		self.grand_total_in_words = money_in_words(self.grand_total)

	@vmraid.whitelist()
	def create_fees(self):
		self.db_set("fee_creation_status", "In Process")
		vmraid.publish_realtime(
			"fee_schedule_progress", {"progress": "0", "reload": 1}, user=vmraid.session.user
		)

		total_records = sum([int(d.total_students) for d in self.student_groups])
		if total_records > 10:
			vmraid.msgprint(
				_(
					"""Fee records will be created in the background.
				In case of any error the error message will be updated in the Schedule."""
				)
			)
			enqueue(
				generate_fee, queue="default", timeout=6000, event="generate_fee", fee_schedule=self.name
			)
		else:
			generate_fee(self.name)


def generate_fee(fee_schedule):
	doc = vmraid.get_doc("Fee Schedule", fee_schedule)
	error = False
	total_records = sum([int(d.total_students) for d in doc.student_groups])
	created_records = 0

	if not total_records:
		vmraid.throw(_("Please setup Students under Student Groups"))

	for d in doc.student_groups:
		students = get_students(
			d.student_group, doc.academic_year, doc.academic_term, doc.student_category
		)
		for student in students:
			try:
				fees_doc = get_mapped_doc(
					"Fee Schedule",
					fee_schedule,
					{"Fee Schedule": {"doctype": "Fees", "field_map": {"name": "Fee Schedule"}}},
				)
				fees_doc.posting_date = doc.posting_date
				fees_doc.student = student.student
				fees_doc.student_name = student.student_name
				fees_doc.program = student.program
				fees_doc.student_batch = student.student_batch_name
				fees_doc.send_payment_request = doc.send_email
				fees_doc.save()
				fees_doc.submit()
				created_records += 1
				vmraid.publish_realtime(
					"fee_schedule_progress",
					{"progress": str(int(created_records * 100 / total_records))},
					user=vmraid.session.user,
				)

			except Exception as e:
				error = True
				err_msg = vmraid.local.message_log and "\n\n".join(vmraid.local.message_log) or cstr(e)

	if error:
		vmraid.db.rollback()
		vmraid.db.set_value("Fee Schedule", fee_schedule, "fee_creation_status", "Failed")
		vmraid.db.set_value("Fee Schedule", fee_schedule, "error_log", err_msg)

	else:
		vmraid.db.set_value("Fee Schedule", fee_schedule, "fee_creation_status", "Successful")
		vmraid.db.set_value("Fee Schedule", fee_schedule, "error_log", None)

	vmraid.publish_realtime(
		"fee_schedule_progress", {"progress": "100", "reload": 1}, user=vmraid.session.user
	)


def get_students(student_group, academic_year, academic_term=None, student_category=None):
	conditions = ""
	if student_category:
		conditions = " and pe.student_category={}".format(vmraid.db.escape(student_category))
	if academic_term:
		conditions = " and pe.academic_term={}".format(vmraid.db.escape(academic_term))

	students = vmraid.db.sql(
		"""
		select pe.student, pe.student_name, pe.program, pe.student_batch_name
		from `tabStudent Group Student` sgs, `tabProgram Enrollment` pe
		where
			pe.student = sgs.student and pe.academic_year = %s
			and sgs.parent = %s and sgs.active = 1
			{conditions}
		""".format(
			conditions=conditions
		),
		(academic_year, student_group),
		as_dict=1,
	)
	return students


@vmraid.whitelist()
def get_total_students(student_group, academic_year, academic_term=None, student_category=None):
	total_students = get_students(student_group, academic_year, academic_term, student_category)
	return len(total_students)


@vmraid.whitelist()
def get_fee_structure(source_name, target_doc=None):
	fee_request = get_mapped_doc(
		"Fee Structure",
		source_name,
		{"Fee Structure": {"doctype": "Fee Schedule"}},
		ignore_permissions=True,
	)
	return fee_request
