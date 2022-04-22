# Copyright (c) 2015, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt

# For license information, please see license.txt


import vmraid
from vmraid import _
from vmraid.model.document import Document
from vmraid.model.naming import append_number_if_name_exists
from vmraid.utils import validate_email_address

from erpadda.hr.doctype.interview.interview import get_interviewers


class DuplicationError(vmraid.ValidationError):
	pass


class JobApplicant(Document):
	def onload(self):
		job_offer = vmraid.get_all("Job Offer", filters={"job_applicant": self.name})
		if job_offer:
			self.get("__onload").job_offer = job_offer[0].name

	def autoname(self):
		self.name = self.email_id

		# applicant can apply more than once for a different job title or reapply
		if vmraid.db.exists("Job Applicant", self.name):
			self.name = append_number_if_name_exists("Job Applicant", self.name)

	def validate(self):
		if self.email_id:
			validate_email_address(self.email_id, True)

		if self.employee_referral:
			self.set_status_for_employee_referral()

		if not self.applicant_name and self.email_id:
			guess = self.email_id.split("@")[0]
			self.applicant_name = " ".join([p.capitalize() for p in guess.split(".")])

	def set_status_for_employee_referral(self):
		emp_ref = vmraid.get_doc("Employee Referral", self.employee_referral)
		if self.status in ["Open", "Replied", "Hold"]:
			emp_ref.db_set("status", "In Process")
		elif self.status in ["Accepted", "Rejected"]:
			emp_ref.db_set("status", self.status)


@vmraid.whitelist()
def create_interview(doc, interview_round):
	import json

	if isinstance(doc, str):
		doc = json.loads(doc)
		doc = vmraid.get_doc(doc)

	round_designation = vmraid.db.get_value("Interview Round", interview_round, "designation")

	if round_designation and doc.designation and round_designation != doc.designation:
		vmraid.throw(
			_("Interview Round {0} is only applicable for the Designation {1}").format(
				interview_round, round_designation
			)
		)

	interview = vmraid.new_doc("Interview")
	interview.interview_round = interview_round
	interview.job_applicant = doc.name
	interview.designation = doc.designation
	interview.resume_link = doc.resume_link
	interview.job_opening = doc.job_title
	interviewer_detail = get_interviewers(interview_round)

	for d in interviewer_detail:
		interview.append("interview_details", {"interviewer": d.interviewer})
	return interview


@vmraid.whitelist()
def get_interview_details(job_applicant):
	interview_details = vmraid.db.get_all(
		"Interview",
		filters={"job_applicant": job_applicant, "docstatus": ["!=", 2]},
		fields=["name", "interview_round", "expected_average_rating", "average_rating", "status"],
	)
	interview_detail_map = {}
	meta = vmraid.get_meta("Interview")
	number_of_stars = meta.get_options("expected_average_rating") or 5

	for detail in interview_details:
		detail.expected_average_rating = (
			detail.expected_average_rating * number_of_stars if detail.expected_average_rating else 0
		)
		detail.average_rating = detail.average_rating * number_of_stars if detail.average_rating else 0

		interview_detail_map[detail.name] = detail

	return {"interviews": interview_detail_map, "stars": number_of_stars}
