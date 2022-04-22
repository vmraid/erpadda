# Copyright (c) 2019, VMRaid and contributors
# For license information, please see license.txt


from collections import Counter

import vmraid
from vmraid import _
from vmraid.model.document import Document
from vmraid.utils import get_url, getdate
from vmraid.utils.verified_command import get_signed_params


class Appointment(Document):
	def find_lead_by_email(self):
		lead_list = vmraid.get_list(
			"Lead", filters={"email_id": self.customer_email}, ignore_permissions=True
		)
		if lead_list:
			return lead_list[0].name
		return None

	def find_customer_by_email(self):
		customer_list = vmraid.get_list(
			"Customer", filters={"email_id": self.customer_email}, ignore_permissions=True
		)
		if customer_list:
			return customer_list[0].name
		return None

	def before_insert(self):
		number_of_appointments_in_same_slot = vmraid.db.count(
			"Appointment", filters={"scheduled_time": self.scheduled_time}
		)
		number_of_agents = vmraid.db.get_single_value("Appointment Booking Settings", "number_of_agents")
		if not number_of_agents == 0:
			if number_of_appointments_in_same_slot >= number_of_agents:
				vmraid.throw(_("Time slot is not available"))
		# Link lead
		if not self.party:
			lead = self.find_lead_by_email()
			customer = self.find_customer_by_email()
			if customer:
				self.appointment_with = "Customer"
				self.party = customer
			else:
				self.appointment_with = "Lead"
				self.party = lead

	def after_insert(self):
		if self.party:
			# Create Calendar event
			self.auto_assign()
			self.create_calendar_event()
		else:
			# Set status to unverified
			self.status = "Unverified"
			# Send email to confirm
			self.send_confirmation_email()

	def send_confirmation_email(self):
		verify_url = self._get_verify_url()
		template = "confirm_appointment"
		args = {
			"link": verify_url,
			"site_url": vmraid.utils.get_url(),
			"full_name": self.customer_name,
		}
		vmraid.sendmail(
			recipients=[self.customer_email],
			template=template,
			args=args,
			subject=_("Appointment Confirmation"),
		)
		if vmraid.session.user == "Guest":
			vmraid.msgprint(_("Please check your email to confirm the appointment"))
		else:
			vmraid.msgprint(
				_("Appointment was created. But no lead was found. Please check the email to confirm")
			)

	def on_change(self):
		# Sync Calendar
		if not self.calendar_event:
			return
		cal_event = vmraid.get_doc("Event", self.calendar_event)
		cal_event.starts_on = self.scheduled_time
		cal_event.save(ignore_permissions=True)

	def set_verified(self, email):
		if not email == self.customer_email:
			vmraid.throw(_("Email verification failed."))
		# Create new lead
		self.create_lead_and_link()
		# Remove unverified status
		self.status = "Open"
		# Create calender event
		self.auto_assign()
		self.create_calendar_event()
		self.save(ignore_permissions=True)
		vmraid.db.commit()

	def create_lead_and_link(self):
		# Return if already linked
		if self.party:
			return
		lead = vmraid.get_doc(
			{
				"doctype": "Lead",
				"lead_name": self.customer_name,
				"email_id": self.customer_email,
				"notes": self.customer_details,
				"phone": self.customer_phone_number,
			}
		)
		lead.insert(ignore_permissions=True)
		# Link lead
		self.party = lead.name

	def auto_assign(self):
		from vmraid.desk.form.assign_to import add as add_assignemnt

		existing_assignee = self.get_assignee_from_latest_opportunity()
		if existing_assignee:
			# If the latest opportunity is assigned to someone
			# Assign the appointment to the same
			add_assignemnt({"doctype": self.doctype, "name": self.name, "assign_to": [existing_assignee]})
			return
		if self._assign:
			return
		available_agents = _get_agents_sorted_by_asc_workload(getdate(self.scheduled_time))
		for agent in available_agents:
			if _check_agent_availability(agent, self.scheduled_time):
				agent = agent[0]
				add_assignemnt({"doctype": self.doctype, "name": self.name, "assign_to": [agent]})
			break

	def get_assignee_from_latest_opportunity(self):
		if not self.party:
			return None
		if not vmraid.db.exists("Lead", self.party):
			return None
		opporutnities = vmraid.get_list(
			"Opportunity",
			filters={
				"party_name": self.party,
			},
			ignore_permissions=True,
			order_by="creation desc",
		)
		if not opporutnities:
			return None
		latest_opportunity = vmraid.get_doc("Opportunity", opporutnities[0].name)
		assignee = latest_opportunity._assign
		if not assignee:
			return None
		assignee = vmraid.parse_json(assignee)[0]
		return assignee

	def create_calendar_event(self):
		if self.calendar_event:
			return
		appointment_event = vmraid.get_doc(
			{
				"doctype": "Event",
				"subject": " ".join(["Appointment with", self.customer_name]),
				"starts_on": self.scheduled_time,
				"status": "Open",
				"type": "Public",
				"send_reminder": vmraid.db.get_single_value("Appointment Booking Settings", "email_reminders"),
				"event_participants": [
					dict(reference_doctype=self.appointment_with, reference_docname=self.party)
				],
			}
		)
		employee = _get_employee_from_user(self._assign)
		if employee:
			appointment_event.append(
				"event_participants", dict(reference_doctype="Employee", reference_docname=employee.name)
			)
		appointment_event.insert(ignore_permissions=True)
		self.calendar_event = appointment_event.name
		self.save(ignore_permissions=True)

	def _get_verify_url(self):
		verify_route = "/book_appointment/verify"
		params = {"email": self.customer_email, "appointment": self.name}
		return get_url(verify_route + "?" + get_signed_params(params))


def _get_agents_sorted_by_asc_workload(date):
	appointments = vmraid.db.get_list("Appointment", fields="*")
	agent_list = _get_agent_list_as_strings()
	if not appointments:
		return agent_list
	appointment_counter = Counter(agent_list)
	for appointment in appointments:
		assigned_to = vmraid.parse_json(appointment._assign)
		if not assigned_to:
			continue
		if (assigned_to[0] in agent_list) and getdate(appointment.scheduled_time) == date:
			appointment_counter[assigned_to[0]] += 1
	sorted_agent_list = appointment_counter.most_common()
	sorted_agent_list.reverse()
	return sorted_agent_list


def _get_agent_list_as_strings():
	agent_list_as_strings = []
	agent_list = vmraid.get_doc("Appointment Booking Settings").agent_list
	for agent in agent_list:
		agent_list_as_strings.append(agent.user)
	return agent_list_as_strings


def _check_agent_availability(agent_email, scheduled_time):
	appointemnts_at_scheduled_time = vmraid.get_list(
		"Appointment", filters={"scheduled_time": scheduled_time}
	)
	for appointment in appointemnts_at_scheduled_time:
		if appointment._assign == agent_email:
			return False
	return True


def _get_employee_from_user(user):
	employee_docname = vmraid.db.get_value("Employee", {"user_id": user})
	if employee_docname:
		return vmraid.get_doc("Employee", employee_docname)
	return None
