# Copyright (c) 2018, VMRaid and contributors
# For license information, please see license.txt


import vmraid
from vmraid import _
from vmraid.model.document import Document
from vmraid.utils import strip


class CouponCode(Document):
	def autoname(self):
		self.coupon_name = strip(self.coupon_name)
		self.name = self.coupon_name

		if not self.coupon_code:
			if self.coupon_type == "Promotional":
				self.coupon_code = "".join(i for i in self.coupon_name if not i.isdigit())[0:8].upper()
			elif self.coupon_type == "Gift Card":
				self.coupon_code = vmraid.generate_hash()[:10].upper()

	def validate(self):
		if self.coupon_type == "Gift Card":
			self.maximum_use = 1
			if not self.customer:
				vmraid.throw(_("Please select the customer."))
