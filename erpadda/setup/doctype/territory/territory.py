# Copyright (c) 2015, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid
from vmraid import _
from vmraid.utils import flt
from vmraid.utils.nestedset import NestedSet, get_root_of


class Territory(NestedSet):
	nsm_parent_field = "parent_territory"

	def validate(self):
		if not self.parent_territory:
			self.parent_territory = get_root_of("Territory")

		for d in self.get("targets") or []:
			if not flt(d.target_qty) and not flt(d.target_amount):
				vmraid.throw(_("Either target qty or target amount is mandatory"))

	def on_update(self):
		super(Territory, self).on_update()
		self.validate_one_root()


def on_doctype_update():
	vmraid.db.add_index("Territory", ["lft", "rgt"])
