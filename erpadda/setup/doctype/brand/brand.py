# Copyright (c) 2015, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import copy

import vmraid
from vmraid.model.document import Document


class Brand(Document):
	pass


def get_brand_defaults(item, company):
	item = vmraid.get_cached_doc("Item", item)
	if item.brand:
		brand = vmraid.get_cached_doc("Brand", item.brand)

		for d in brand.brand_defaults or []:
			if d.company == company:
				row = copy.deepcopy(d.as_dict())
				row.pop("name")
				return row

	return vmraid._dict()
