# Copyright (c) 2021, VMRaid and contributors
# For license information, please see license.txt


import json

import vmraid
from vmraid.model.document import Document


class InterviewRound(Document):
	pass


@vmraid.whitelist()
def create_interview(doc):
	if isinstance(doc, str):
		doc = json.loads(doc)
		doc = vmraid.get_doc(doc)

	interview = vmraid.new_doc("Interview")
	interview.interview_round = doc.name
	interview.designation = doc.designation

	if doc.interviewers:
		interview.interview_details = []
		for data in doc.interviewers:
			interview.append("interview_details", {"interviewer": data.user})
	return interview
