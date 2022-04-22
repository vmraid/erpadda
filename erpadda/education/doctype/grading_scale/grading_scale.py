# Copyright (c) 2015, VMRaid and contributors
# For license information, please see license.txt


import vmraid
from vmraid import _
from vmraid.model.document import Document
from vmraid.utils import cint


class GradingScale(Document):
	def validate(self):
		thresholds = []
		for d in self.intervals:
			if d.threshold in thresholds:
				vmraid.throw(_("Treshold {0}% appears more than once").format(d.threshold))
			else:
				thresholds.append(cint(d.threshold))
		if 0 not in thresholds:
			vmraid.throw(_("Please define grade for Threshold 0%"))
