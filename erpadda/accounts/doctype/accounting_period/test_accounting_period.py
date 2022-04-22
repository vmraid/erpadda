# Copyright (c) 2018, VMRaid and Contributors
# See license.txt

import unittest

import vmraid
from vmraid.utils import add_months, nowdate

from erpadda.accounts.doctype.accounting_period.accounting_period import OverlapError
from erpadda.accounts.doctype.sales_invoice.test_sales_invoice import create_sales_invoice
from erpadda.accounts.general_ledger import ClosedAccountingPeriod

test_dependencies = ["Item"]


class TestAccountingPeriod(unittest.TestCase):
	def test_overlap(self):
		ap1 = create_accounting_period(
			start_date="2018-04-01", end_date="2018-06-30", company="Wind Power LLC"
		)
		ap1.save()

		ap2 = create_accounting_period(
			start_date="2018-06-30",
			end_date="2018-07-10",
			company="Wind Power LLC",
			period_name="Test Accounting Period 1",
		)
		self.assertRaises(OverlapError, ap2.save)

	def test_accounting_period(self):
		ap1 = create_accounting_period(period_name="Test Accounting Period 2")
		ap1.save()

		doc = create_sales_invoice(
			do_not_submit=1, cost_center="_Test Company - _TC", warehouse="Stores - _TC"
		)
		self.assertRaises(ClosedAccountingPeriod, doc.submit)

	def tearDown(self):
		for d in vmraid.get_all("Accounting Period"):
			vmraid.delete_doc("Accounting Period", d.name)


def create_accounting_period(**args):
	args = vmraid._dict(args)

	accounting_period = vmraid.new_doc("Accounting Period")
	accounting_period.start_date = args.start_date or nowdate()
	accounting_period.end_date = args.end_date or add_months(nowdate(), 1)
	accounting_period.company = args.company or "_Test Company"
	accounting_period.period_name = args.period_name or "_Test_Period_Name_1"
	accounting_period.append("closed_documents", {"document_type": "Sales Invoice", "closed": 1})

	return accounting_period
