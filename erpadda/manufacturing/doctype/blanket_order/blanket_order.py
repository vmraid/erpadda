# Copyright (c) 2018, VMRaid and contributors
# For license information, please see license.txt


import vmraid
from vmraid import _
from vmraid.model.document import Document
from vmraid.model.mapper import get_mapped_doc
from vmraid.utils import flt, getdate

from erpadda.stock.doctype.item.item import get_item_defaults


class BlanketOrder(Document):
	def validate(self):
		self.validate_dates()
		self.validate_duplicate_items()

	def validate_dates(self):
		if getdate(self.from_date) > getdate(self.to_date):
			vmraid.throw(_("From date cannot be greater than To date"))

	def validate_duplicate_items(self):
		item_list = []
		for item in self.items:
			if item.item_code in item_list:
				vmraid.throw(_("Note: Item {0} added multiple times").format(vmraid.bold(item.item_code)))
			item_list.append(item.item_code)

	def update_ordered_qty(self):
		ref_doctype = "Sales Order" if self.blanket_order_type == "Selling" else "Purchase Order"
		item_ordered_qty = vmraid._dict(
			vmraid.db.sql(
				"""
			select trans_item.item_code, sum(trans_item.stock_qty) as qty
			from `tab{0} Item` trans_item, `tab{0}` trans
			where trans.name = trans_item.parent
				and trans_item.blanket_order=%s
				and trans.docstatus=1
				and trans.status not in ('Closed', 'Stopped')
			group by trans_item.item_code
		""".format(
					ref_doctype
				),
				self.name,
			)
		)

		for d in self.items:
			d.db_set("ordered_qty", item_ordered_qty.get(d.item_code, 0))


@vmraid.whitelist()
def make_order(source_name):
	doctype = vmraid.flags.args.doctype

	def update_doc(source_doc, target_doc, source_parent):
		if doctype == "Quotation":
			target_doc.quotation_to = "Customer"
			target_doc.party_name = source_doc.customer

	def update_item(source, target, source_parent):
		target_qty = source.get("qty") - source.get("ordered_qty")
		target.qty = target_qty if not flt(target_qty) < 0 else 0
		item = get_item_defaults(target.item_code, source_parent.company)
		if item:
			target.item_name = item.get("item_name")
			target.description = item.get("description")
			target.uom = item.get("stock_uom")
			target.against_blanket_order = 1
			target.blanket_order = source_name

	target_doc = get_mapped_doc(
		"Blanket Order",
		source_name,
		{
			"Blanket Order": {"doctype": doctype, "postprocess": update_doc},
			"Blanket Order Item": {
				"doctype": doctype + " Item",
				"field_map": {"rate": "blanket_order_rate", "parent": "blanket_order"},
				"postprocess": update_item,
			},
		},
	)
	return target_doc
