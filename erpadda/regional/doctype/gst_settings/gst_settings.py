# Copyright (c) 2017, VMRaid and contributors
# For license information, please see license.txt


import os

import vmraid
from vmraid import _
from vmraid.contacts.doctype.contact.contact import get_default_contact
from vmraid.model.document import Document
from vmraid.utils import date_diff, get_url, nowdate


class EmailMissing(vmraid.ValidationError):
	pass


class GSTSettings(Document):
	def onload(self):
		data = vmraid._dict()
		data.total_addresses = vmraid.db.sql(
			'''select count(*) from tabAddress where country = "India"'''
		)
		data.total_addresses_with_gstin = vmraid.db.sql(
			"""select distinct count(*)
			from tabAddress where country = "India" and ifnull(gstin, '')!='' """
		)
		self.set_onload("data", data)

	def validate(self):
		# Validate duplicate accounts
		self.validate_duplicate_accounts()

	def validate_duplicate_accounts(self):
		account_list = []
		for account in self.get("gst_accounts"):
			for fieldname in ["cgst_account", "sgst_account", "igst_account", "cess_account"]:
				if account.get(fieldname) in account_list:
					vmraid.throw(
						_("Account {0} appears multiple times").format(vmraid.bold(account.get(fieldname)))
					)

				if account.get(fieldname):
					account_list.append(account.get(fieldname))


@vmraid.whitelist()
def send_reminder():
	vmraid.has_permission("GST Settings", throw=True)

	last_sent = vmraid.db.get_single_value("GST Settings", "gstin_email_sent_on")
	if last_sent and date_diff(nowdate(), last_sent) < 3:
		vmraid.throw(_("Please wait 3 days before resending the reminder."))

	vmraid.db.set_value("GST Settings", "GST Settings", "gstin_email_sent_on", nowdate())

	# enqueue if large number of customers, suppliser
	vmraid.enqueue(
		"erpadda.regional.doctype.gst_settings.gst_settings.send_gstin_reminder_to_all_parties"
	)
	vmraid.msgprint(_("Email Reminders will be sent to all parties with email contacts"))


def send_gstin_reminder_to_all_parties():
	parties = []
	for address_name in vmraid.db.sql(
		"""select name
		from tabAddress where country = "India" and ifnull(gstin, '')='' """
	):
		address = vmraid.get_doc("Address", address_name[0])
		for link in address.links:
			party = vmraid.get_doc(link.link_doctype, link.link_name)
			if link.link_doctype in ("Customer", "Supplier"):
				t = (link.link_doctype, link.link_name, address.email_id)
				if not t in parties:
					parties.append(t)

	sent_to = []
	for party in parties:
		# get email from default contact
		try:
			email_id = _send_gstin_reminder(party[0], party[1], party[2], sent_to)
			sent_to.append(email_id)
		except EmailMissing:
			pass


@vmraid.whitelist()
def send_gstin_reminder(party_type, party):
	"""Send GSTIN reminder to one party (called from Customer, Supplier form)"""
	vmraid.has_permission(party_type, throw=True)
	email = _send_gstin_reminder(party_type, party)
	if email:
		vmraid.msgprint(_("Reminder to update GSTIN Sent"), title="Reminder sent", indicator="green")


def _send_gstin_reminder(party_type, party, default_email_id=None, sent_to=None):
	"""Send GST Reminder email"""
	email_id = vmraid.db.get_value("Contact", get_default_contact(party_type, party), "email_id")
	if not email_id:
		# get email from address
		email_id = default_email_id

	if not email_id:
		vmraid.throw(_("Email not found in default contact"), exc=EmailMissing)

	if sent_to and email_id in sent_to:
		return

	vmraid.sendmail(
		subject="Please update your GSTIN",
		recipients=email_id,
		message="""
		<p>Hello,</p>
		<p>Please help us send you GST Ready Invoices.</p>
		<p>
			<a href="{0}?party={1}">
			Click here to update your GSTIN Number in our system
			</a>
		</p>
		<p style="color: #aaa; font-size: 11px; margin-top: 30px;">
			Get your GST Ready ERP system at <a href="https://erpadda.com">https://erpadda.com</a>
			<br>
			ERPAdda is a free and open source ERP system.
		</p>
		""".format(
			os.path.join(get_url(), "/regional/india/update-gstin"), party
		),
	)

	return email_id
