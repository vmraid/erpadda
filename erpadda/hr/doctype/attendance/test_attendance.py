# Copyright (c) 2015, VMRaid and Contributors and Contributors
# See license.txt

import vmraid
from vmraid.tests.utils import VMRaidTestCase
from vmraid.utils import add_days, get_year_ending, get_year_start, getdate, now_datetime, nowdate

from erpadda.hr.doctype.attendance.attendance import (
	DuplicateAttendanceError,
	OverlappingShiftAttendanceError,
	get_month_map,
	get_unmarked_days,
	mark_attendance,
)
from erpadda.hr.doctype.employee.test_employee import make_employee
from erpadda.hr.doctype.leave_application.test_leave_application import get_first_sunday

test_records = vmraid.get_test_records("Attendance")


class TestAttendance(VMRaidTestCase):
	def setUp(self):
		from erpadda.payroll.doctype.salary_slip.test_salary_slip import make_holiday_list

		from_date = get_year_start(getdate())
		to_date = get_year_ending(getdate())
		self.holiday_list = make_holiday_list(from_date=from_date, to_date=to_date)
		vmraid.db.delete("Attendance")

	def test_duplicate_attendance(self):
		employee = make_employee("test_duplicate_attendance@example.com", company="_Test Company")
		date = nowdate()

		mark_attendance(employee, date, "Present")
		attendance = vmraid.get_doc(
			{
				"doctype": "Attendance",
				"employee": employee,
				"attendance_date": date,
				"status": "Absent",
				"company": "_Test Company",
			}
		)

		self.assertRaises(DuplicateAttendanceError, attendance.insert)

	def test_duplicate_attendance_with_shift(self):
		from erpadda.hr.doctype.shift_type.test_shift_type import setup_shift_type

		employee = make_employee("test_duplicate_attendance@example.com", company="_Test Company")
		date = nowdate()

		shift_1 = setup_shift_type(shift_type="Shift 1", start_time="08:00:00", end_time="10:00:00")
		mark_attendance(employee, date, "Present", shift=shift_1.name)

		# attendance record with shift
		attendance = vmraid.get_doc(
			{
				"doctype": "Attendance",
				"employee": employee,
				"attendance_date": date,
				"status": "Absent",
				"company": "_Test Company",
				"shift": shift_1.name,
			}
		)

		self.assertRaises(DuplicateAttendanceError, attendance.insert)

		# attendance record without any shift
		attendance = vmraid.get_doc(
			{
				"doctype": "Attendance",
				"employee": employee,
				"attendance_date": date,
				"status": "Absent",
				"company": "_Test Company",
			}
		)

		self.assertRaises(DuplicateAttendanceError, attendance.insert)

	def test_overlapping_shift_attendance_validation(self):
		from erpadda.hr.doctype.shift_type.test_shift_type import setup_shift_type

		employee = make_employee("test_overlap_attendance@example.com", company="_Test Company")
		date = nowdate()

		shift_1 = setup_shift_type(shift_type="Shift 1", start_time="08:00:00", end_time="10:00:00")
		shift_2 = setup_shift_type(shift_type="Shift 2", start_time="09:30:00", end_time="11:00:00")

		mark_attendance(employee, date, "Present", shift=shift_1.name)

		# attendance record with overlapping shift
		attendance = vmraid.get_doc(
			{
				"doctype": "Attendance",
				"employee": employee,
				"attendance_date": date,
				"status": "Absent",
				"company": "_Test Company",
				"shift": shift_2.name,
			}
		)

		self.assertRaises(OverlappingShiftAttendanceError, attendance.insert)

	def test_allow_attendance_with_different_shifts(self):
		# allows attendance with 2 different non-overlapping shifts
		from erpadda.hr.doctype.shift_type.test_shift_type import setup_shift_type

		employee = make_employee("test_duplicate_attendance@example.com", company="_Test Company")
		date = nowdate()

		shift_1 = setup_shift_type(shift_type="Shift 1", start_time="08:00:00", end_time="10:00:00")
		shift_2 = setup_shift_type(shift_type="Shift 2", start_time="11:00:00", end_time="12:00:00")

		mark_attendance(employee, date, "Present", shift_1.name)
		vmraid.get_doc(
			{
				"doctype": "Attendance",
				"employee": employee,
				"attendance_date": date,
				"status": "Absent",
				"company": "_Test Company",
				"shift": shift_2.name,
			}
		).insert()

	def test_mark_absent(self):
		employee = make_employee("test_mark_absent@example.com")
		date = nowdate()

		attendance = mark_attendance(employee, date, "Absent")
		fetch_attendance = vmraid.get_value(
			"Attendance", {"employee": employee, "attendance_date": date, "status": "Absent"}
		)
		self.assertEqual(attendance, fetch_attendance)

	def test_unmarked_days(self):
		now = now_datetime()
		previous_month = now.month - 1
		first_day = now.replace(day=1).replace(month=previous_month).date()

		employee = make_employee(
			"test_unmarked_days@example.com", date_of_joining=add_days(first_day, -1)
		)
		vmraid.db.set_value("Employee", employee, "holiday_list", self.holiday_list)

		first_sunday = get_first_sunday(self.holiday_list, for_date=first_day)
		mark_attendance(employee, first_day, "Present")
		month_name = get_month_name(first_day)

		unmarked_days = get_unmarked_days(employee, month_name)
		unmarked_days = [getdate(date) for date in unmarked_days]

		# attendance already marked for the day
		self.assertNotIn(first_day, unmarked_days)
		# attendance unmarked
		self.assertIn(getdate(add_days(first_day, 1)), unmarked_days)
		# holiday considered in unmarked days
		self.assertIn(first_sunday, unmarked_days)

	def test_unmarked_days_excluding_holidays(self):
		now = now_datetime()
		previous_month = now.month - 1
		first_day = now.replace(day=1).replace(month=previous_month).date()

		employee = make_employee(
			"test_unmarked_days@example.com", date_of_joining=add_days(first_day, -1)
		)
		vmraid.db.set_value("Employee", employee, "holiday_list", self.holiday_list)

		first_sunday = get_first_sunday(self.holiday_list, for_date=first_day)
		mark_attendance(employee, first_day, "Present")
		month_name = get_month_name(first_day)

		unmarked_days = get_unmarked_days(employee, month_name, exclude_holidays=True)
		unmarked_days = [getdate(date) for date in unmarked_days]

		# attendance already marked for the day
		self.assertNotIn(first_day, unmarked_days)
		# attendance unmarked
		self.assertIn(getdate(add_days(first_day, 1)), unmarked_days)
		# holidays not considered in unmarked days
		self.assertNotIn(first_sunday, unmarked_days)

	def test_unmarked_days_as_per_joining_and_relieving_dates(self):
		now = now_datetime()
		previous_month = now.month - 1
		first_day = now.replace(day=1).replace(month=previous_month).date()

		doj = add_days(first_day, 1)
		relieving_date = add_days(first_day, 5)
		employee = make_employee(
			"test_unmarked_days_as_per_doj@example.com", date_of_joining=doj, relieving_date=relieving_date
		)

		vmraid.db.set_value("Employee", employee, "holiday_list", self.holiday_list)

		attendance_date = add_days(first_day, 2)
		mark_attendance(employee, attendance_date, "Present")
		month_name = get_month_name(first_day)

		unmarked_days = get_unmarked_days(employee, month_name)
		unmarked_days = [getdate(date) for date in unmarked_days]

		# attendance already marked for the day
		self.assertNotIn(attendance_date, unmarked_days)
		# date before doj not in unmarked days
		self.assertNotIn(add_days(doj, -1), unmarked_days)
		# date after relieving not in unmarked days
		self.assertNotIn(add_days(relieving_date, 1), unmarked_days)

	def tearDown(self):
		vmraid.db.rollback()


def get_month_name(date):
	month_number = date.month
	for month, number in get_month_map().items():
		if number == month_number:
			return month
