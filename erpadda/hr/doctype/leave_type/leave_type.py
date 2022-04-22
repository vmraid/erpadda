# Copyright (c) 2015, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid
from vmraid import _
from vmraid.model.document import Document
from vmraid.utils import today


class LeaveType(Document):
	def validate(self):
		if self.is_lwp:
			leave_allocation = vmraid.get_all(
				"Leave Allocation",
				filters={"leave_type": self.name, "from_date": ("<=", today()), "to_date": (">=", today())},
				fields=["name"],
			)
			leave_allocation = [l["name"] for l in leave_allocation]
			if leave_allocation:
				vmraid.throw(
					_(
						"Leave application is linked with leave allocations {0}. Leave application cannot be set as leave without pay"
					).format(", ".join(leave_allocation))
				)  # nosec

		if self.is_lwp and self.is_ppl:
			vmraid.throw(_("Leave Type can be either without pay or partial pay"))

		if self.is_ppl and (
			self.fraction_of_daily_salary_per_leave < 0 or self.fraction_of_daily_salary_per_leave > 1
		):
			vmraid.throw(_("The fraction of Daily Salary per Leave should be between 0 and 1"))
