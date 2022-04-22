# Copyright (c) 2015, VMRaid and contributors
# For license information, please see license.txt


import vmraid
from vmraid import _
from vmraid.model.document import Document
from vmraid.utils import getdate


class Vehicle(Document):
	def validate(self):
		if getdate(self.start_date) > getdate(self.end_date):
			vmraid.throw(_("Insurance Start date should be less than Insurance End date"))
		if getdate(self.carbon_check_date) > getdate():
			vmraid.throw(_("Last carbon check date cannot be a future date"))


def get_timeline_data(doctype, name):
	"""Return timeline for vehicle log"""
	return dict(
		vmraid.db.sql(
			"""select unix_timestamp(date), count(*)
	from `tabVehicle Log` where license_plate=%s
	and date > date_sub(curdate(), interval 1 year)
	group by date""",
			name,
		)
	)
