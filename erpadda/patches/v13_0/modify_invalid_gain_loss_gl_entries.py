import json

import vmraid


def execute():
	vmraid.reload_doc("accounts", "doctype", "purchase_invoice_advance")
	vmraid.reload_doc("accounts", "doctype", "sales_invoice_advance")

	purchase_invoices = vmraid.db.sql(
		"""
		select
			parenttype as type, parent as name
		from
			`tabPurchase Invoice Advance`
		where
			ref_exchange_rate = 1
			and docstatus = 1
			and ifnull(exchange_gain_loss, 0) != 0
		group by
			parent
	""",
		as_dict=1,
	)

	sales_invoices = vmraid.db.sql(
		"""
		select
			parenttype as type, parent as name
		from
			`tabSales Invoice Advance`
		where
			ref_exchange_rate = 1
			and docstatus = 1
			and ifnull(exchange_gain_loss, 0) != 0
		group by
			parent
	""",
		as_dict=1,
	)

	if purchase_invoices + sales_invoices:
		vmraid.log_error(json.dumps(purchase_invoices + sales_invoices, indent=2), title="Patch Log")

	acc_frozen_upto = vmraid.db.get_value("Accounts Settings", None, "acc_frozen_upto")
	if acc_frozen_upto:
		vmraid.db.set_value("Accounts Settings", None, "acc_frozen_upto", None)

	for invoice in purchase_invoices + sales_invoices:
		try:
			doc = vmraid.get_doc(invoice.type, invoice.name)
			doc.docstatus = 2
			doc.make_gl_entries()
			for advance in doc.advances:
				if advance.ref_exchange_rate == 1:
					advance.db_set("exchange_gain_loss", 0, False)
			doc.docstatus = 1
			doc.make_gl_entries()
			vmraid.db.commit()
		except Exception:
			vmraid.db.rollback()
			print(f"Failed to correct gl entries of {invoice.name}")

	if acc_frozen_upto:
		vmraid.db.set_value("Accounts Settings", None, "acc_frozen_upto", acc_frozen_upto)
