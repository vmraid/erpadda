# Copyright (c) 2017, VMRaid and contributors
# For license information, please see license.txt


import vmraid
from vmraid import _
from vmraid.model.document import Document


class ProjectType(Document):
	def on_trash(self):
		if self.name == "External":
			vmraid.throw(_("You cannot delete Project Type 'External'"))
