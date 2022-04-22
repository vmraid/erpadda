import vmraid
from vmraid.email import sendmail_to_system_managers


def execute():
	vmraid.reload_doc("stock", "doctype", "item")
	vmraid.reload_doc("stock", "doctype", "customs_tariff_number")
	vmraid.reload_doc("accounts", "doctype", "payment_terms_template")
	vmraid.reload_doc("accounts", "doctype", "payment_schedule")

	company = vmraid.get_all("Company", filters={"country": "India"})
	if not company:
		return

	vmraid.reload_doc("regional", "doctype", "gst_settings")
	vmraid.reload_doc("regional", "doctype", "gst_hsn_code")

	for report_name in (
		"GST Sales Register",
		"GST Purchase Register",
		"GST Itemised Sales Register",
		"GST Itemised Purchase Register",
	):

		vmraid.reload_doc("regional", "report", vmraid.scrub(report_name))

	from erpadda.regional.india.setup import setup

	delete_custom_field_tax_id_if_exists()
	setup(patch=True)
	send_gst_update_email()


def delete_custom_field_tax_id_if_exists():
	for field in vmraid.db.sql_list(
		"""select name from `tabCustom Field` where fieldname='tax_id'
		and dt in ('Sales Order', 'Sales Invoice', 'Delivery Note')"""
	):
		vmraid.delete_doc("Custom Field", field, ignore_permissions=True)
		vmraid.db.commit()


def send_gst_update_email():
	message = """Hello,

<p>ERPAdda is now GST Ready!</p>

<p>To start making GST Invoices from 1st of July, you just need to create new Tax Accounts,
Templates and update your Customer's and Supplier's GST Numbers.</p>

<p>Please refer {gst_document_link} to know more about how to setup and implement GST in ERPAdda.</p>

<p>Please contact us at support@erpadda.com, if you have any questions.</p>

<p>Thanks,</p>
ERPAdda Team.
	""".format(
		gst_document_link="<a href='http://vmraid.github.io/erpadda/user/manual/en/regional/india/'> ERPAdda GST Document </a>"
	)

	try:
		sendmail_to_system_managers("[Important] ERPAdda GST updates", message)
	except Exception as e:
		pass
