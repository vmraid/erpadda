# Copyright (c) 2015, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid
from vmraid import _
from vmraid.model.document import Document
from vmraid.utils import (
	add_days,
	cint,
	comma_and,
	flt,
	formatdate,
	getdate,
	time_diff_in_seconds,
	to_timedelta,
)

from erpadda.support.doctype.issue.issue import get_holidays


class WorkstationHolidayError(vmraid.ValidationError):
	pass


class NotInWorkingHoursError(vmraid.ValidationError):
	pass


class OverlapError(vmraid.ValidationError):
	pass


class Workstation(Document):
	def validate(self):
		self.hour_rate = (
			flt(self.hour_rate_labour)
			+ flt(self.hour_rate_electricity)
			+ flt(self.hour_rate_consumable)
			+ flt(self.hour_rate_rent)
		)

	def on_update(self):
		self.validate_overlap_for_operation_timings()
		self.update_bom_operation()

	def validate_overlap_for_operation_timings(self):
		"""Check if there is no overlap in setting Workstation Operating Hours"""
		for d in self.get("working_hours"):
			existing = vmraid.db.sql_list(
				"""select idx from `tabWorkstation Working Hour`
				where parent = %s and name != %s
					and (
						(start_time between %s and %s) or
						(end_time between %s and %s) or
						(%s between start_time and end_time))
				""",
				(self.name, d.name, d.start_time, d.end_time, d.start_time, d.end_time, d.start_time),
			)

			if existing:
				vmraid.throw(
					_("Row #{0}: Timings conflicts with row {1}").format(d.idx, comma_and(existing)), OverlapError
				)

	def update_bom_operation(self):
		bom_list = vmraid.db.sql(
			"""select DISTINCT parent from `tabBOM Operation`
			where workstation = %s and parenttype = 'routing' """,
			self.name,
		)

		for bom_no in bom_list:
			vmraid.db.sql(
				"""update `tabBOM Operation` set hour_rate = %s
				where parent = %s and workstation = %s""",
				(self.hour_rate, bom_no[0], self.name),
			)

	def validate_workstation_holiday(self, schedule_date, skip_holiday_list_check=False):
		if not skip_holiday_list_check and (
			not self.holiday_list
			or cint(vmraid.db.get_single_value("Manufacturing Settings", "allow_production_on_holidays"))
		):
			return schedule_date

		if schedule_date in tuple(get_holidays(self.holiday_list)):
			schedule_date = add_days(schedule_date, 1)
			self.validate_workstation_holiday(schedule_date, skip_holiday_list_check=True)

		return schedule_date


@vmraid.whitelist()
def get_default_holiday_list():
	return vmraid.get_cached_value(
		"Company", vmraid.defaults.get_user_default("Company"), "default_holiday_list"
	)


def check_if_within_operating_hours(workstation, operation, from_datetime, to_datetime):
	if from_datetime and to_datetime:
		if not cint(
			vmraid.db.get_value("Manufacturing Settings", "None", "allow_production_on_holidays")
		):
			check_workstation_for_holiday(workstation, from_datetime, to_datetime)

		if not cint(vmraid.db.get_value("Manufacturing Settings", None, "allow_overtime")):
			is_within_operating_hours(workstation, operation, from_datetime, to_datetime)


def is_within_operating_hours(workstation, operation, from_datetime, to_datetime):
	operation_length = time_diff_in_seconds(to_datetime, from_datetime)
	workstation = vmraid.get_doc("Workstation", workstation)

	if not workstation.working_hours:
		return

	for working_hour in workstation.working_hours:
		if working_hour.start_time and working_hour.end_time:
			slot_length = (
				to_timedelta(working_hour.end_time or "") - to_timedelta(working_hour.start_time or "")
			).total_seconds()
			if slot_length >= operation_length:
				return

	vmraid.throw(
		_(
			"Operation {0} longer than any available working hours in workstation {1}, break down the operation into multiple operations"
		).format(operation, workstation.name),
		NotInWorkingHoursError,
	)


def check_workstation_for_holiday(workstation, from_datetime, to_datetime):
	holiday_list = vmraid.db.get_value("Workstation", workstation, "holiday_list")
	if holiday_list and from_datetime and to_datetime:
		applicable_holidays = []
		for d in vmraid.db.sql(
			"""select holiday_date from `tabHoliday` where parent = %s
			and holiday_date between %s and %s """,
			(holiday_list, getdate(from_datetime), getdate(to_datetime)),
		):
			applicable_holidays.append(formatdate(d[0]))

		if applicable_holidays:
			vmraid.throw(
				_("Workstation is closed on the following dates as per Holiday List: {0}").format(holiday_list)
				+ "\n"
				+ "\n".join(applicable_holidays),
				WorkstationHolidayError,
			)
