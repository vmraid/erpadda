# Copyright (c) 2021, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt
import vmraid

from erpadda.controllers.status_updater import OverAllowanceError


def execute():
	vmraid.reload_doc("stock", "doctype", "purchase_receipt")
	vmraid.reload_doc("stock", "doctype", "purchase_receipt_item")
	vmraid.reload_doc("stock", "doctype", "delivery_note")
	vmraid.reload_doc("stock", "doctype", "delivery_note_item")
	vmraid.reload_doc("stock", "doctype", "stock_settings")

	def update_from_return_docs(doctype):
		for return_doc in vmraid.get_all(
			doctype, filters={"is_return": 1, "docstatus": 1, "return_against": ("!=", "")}
		):
			# Update original receipt/delivery document from return
			return_doc = vmraid.get_cached_doc(doctype, return_doc.name)
			try:
				return_doc.update_prevdoc_status()
			except OverAllowanceError:
				vmraid.db.rollback()
				continue

			return_against = vmraid.get_doc(doctype, return_doc.return_against)
			return_against.update_billing_status()
			vmraid.db.commit()

	# Set received qty in stock uom in PR, as returned qty is checked against it
	vmraid.db.sql(
		""" update `tabPurchase Receipt Item`
		set received_stock_qty = received_qty * conversion_factor
		where docstatus = 1 """
	)

	for doctype in ("Purchase Receipt", "Delivery Note"):
		update_from_return_docs(doctype)
