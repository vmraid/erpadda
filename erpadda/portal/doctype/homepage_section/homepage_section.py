# Copyright (c) 2019, VMRaid and contributors
# For license information, please see license.txt


from vmraid.model.document import Document
from vmraid.utils import cint


class HomepageSection(Document):
	@property
	def column_value(self):
		return cint(12 / cint(self.no_of_columns or 3))
