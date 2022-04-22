# Copyright (c) 2015, VMRaid and contributors
# For license information, please see license.txt


import vmraid
from vmraid.model.document import Document
from vmraid.website.utils import delete_page_cache


class Homepage(Document):
	def validate(self):
		if not self.description:
			self.description = vmraid._("This is an example website auto-generated from ERPAdda")
		delete_page_cache("home")

	def setup_items(self):
		for d in vmraid.get_all(
			"Website Item",
			fields=["name", "item_name", "description", "image", "route"],
			filters={"published": 1},
			limit=3,
		):

			doc = vmraid.get_doc("Website Item", d.name)
			if not doc.route:
				# set missing route
				doc.save()
			self.append(
				"products",
				dict(
					item_code=d.name,
					item_name=d.item_name,
					description=d.description,
					image=d.image,
					route=d.route,
				),
			)
