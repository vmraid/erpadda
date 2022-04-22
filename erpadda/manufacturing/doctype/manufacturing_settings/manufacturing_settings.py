# Copyright (c) 2015, VMRaid and Contributors and contributors
# For license information, please see license.txt


import vmraid
from dateutil.relativedelta import relativedelta
from vmraid.model.document import Document
from vmraid.utils import cint


class ManufacturingSettings(Document):
	pass


def get_mins_between_operations():
	return relativedelta(
		minutes=cint(vmraid.db.get_single_value("Manufacturing Settings", "mins_between_operations"))
		or 10
	)


@vmraid.whitelist()
def is_material_consumption_enabled():
	if not hasattr(vmraid.local, "material_consumption"):
		vmraid.local.material_consumption = cint(
			vmraid.db.get_single_value("Manufacturing Settings", "material_consumption")
		)

	return vmraid.local.material_consumption
