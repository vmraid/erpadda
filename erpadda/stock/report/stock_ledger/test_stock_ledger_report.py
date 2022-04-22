# Copyright (c) 2022, VMRaid and Contributors
# See license.txt

import vmraid
from vmraid.tests.utils import VMRaidTestCase
from vmraid.utils import add_days, today

from erpadda.maintenance.doctype.maintenance_schedule.test_maintenance_schedule import (
	make_serial_item_with_serial,
)
from erpadda.stock.doctype.delivery_note.test_delivery_note import create_delivery_note
from erpadda.stock.doctype.serial_no.serial_no import get_serial_nos
from erpadda.stock.report.stock_ledger.stock_ledger import execute


class TestStockLedgerReeport(VMRaidTestCase):
	def setUp(self) -> None:
		make_serial_item_with_serial("_Test Stock Report Serial Item")
		self.filters = vmraid._dict(
			company="_Test Company",
			from_date=today(),
			to_date=add_days(today(), 30),
			item_code="_Test Stock Report Serial Item",
		)

	def tearDown(self) -> None:
		vmraid.db.rollback()

	def test_serial_balance(self):
		item_code = "_Test Stock Report Serial Item"
		# Checks serials which were added through stock in entry.
		columns, data = execute(self.filters)
		self.assertEqual(data[0].in_qty, 2)
		serials_added = get_serial_nos(data[0].serial_no)
		self.assertEqual(len(serials_added), 2)
		# Stock out entry for one of the serials.
		dn = create_delivery_note(item=item_code, serial_no=serials_added[1])
		self.filters.voucher_no = dn.name
		columns, data = execute(self.filters)
		self.assertEqual(data[0].out_qty, -1)
		self.assertEqual(data[0].serial_no, serials_added[1])
		self.assertEqual(data[0].balance_serial_no, serials_added[0])
