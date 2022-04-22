# Copyright (c) 2015, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import unittest

import vmraid
from vmraid.utils import now_datetime

from erpadda.accounts.doctype.fiscal_year.fiscal_year import FiscalYearIncorrectDate

test_ignore = ["Company"]


class TestFiscalYear(unittest.TestCase):
	def test_extra_year(self):
		if vmraid.db.exists("Fiscal Year", "_Test Fiscal Year 2000"):
			vmraid.delete_doc("Fiscal Year", "_Test Fiscal Year 2000")

		fy = vmraid.get_doc(
			{
				"doctype": "Fiscal Year",
				"year": "_Test Fiscal Year 2000",
				"year_end_date": "2002-12-31",
				"year_start_date": "2000-04-01",
			}
		)

		self.assertRaises(FiscalYearIncorrectDate, fy.insert)


def test_record_generator():
	test_records = [
		{
			"doctype": "Fiscal Year",
			"year": "_Test Short Fiscal Year 2011",
			"is_short_year": 1,
			"year_end_date": "2011-04-01",
			"year_start_date": "2011-12-31",
		}
	]

	start = 2012
	end = now_datetime().year + 5
	for year in range(start, end):
		test_records.append(
			{
				"doctype": "Fiscal Year",
				"year": f"_Test Fiscal Year {year}",
				"year_start_date": f"{year}-01-01",
				"year_end_date": f"{year}-12-31",
			}
		)

	return test_records


test_records = test_record_generator()
