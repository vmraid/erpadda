# Copyright (c) 2015, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid
from vmraid.contacts.address_and_contact import load_address_and_contact
from vmraid.utils import cstr, filter_strip_join
from vmraid.website.website_generator import WebsiteGenerator


class SalesPartner(WebsiteGenerator):
	website = vmraid._dict(
		page_title_field="partner_name",
		condition_field="show_in_website",
		template="templates/generators/sales_partner.html",
	)

	def onload(self):
		"""Load address and contacts in `__onload`"""
		load_address_and_contact(self)

	def autoname(self):
		self.name = self.partner_name

	def validate(self):
		if not self.route:
			self.route = "partners/" + self.scrub(self.partner_name)
		super(SalesPartner, self).validate()
		if self.partner_website and not self.partner_website.startswith("http"):
			self.partner_website = "http://" + self.partner_website

	def get_context(self, context):
		address = vmraid.db.get_value(
			"Address", {"sales_partner": self.name, "is_primary_address": 1}, "*", as_dict=True
		)
		if address:
			city_state = ", ".join(filter(None, [address.city, address.state]))
			address_rows = [
				address.address_line1,
				address.address_line2,
				city_state,
				address.pincode,
				address.country,
			]

			context.update(
				{
					"email": address.email_id,
					"partner_address": filter_strip_join(address_rows, "\n<br>"),
					"phone": filter_strip_join(cstr(address.phone).split(","), "\n<br>"),
				}
			)

		return context
