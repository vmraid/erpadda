import json
import unittest

import vmraid

from erpadda.controllers.item_variant import copy_attributes_to_variant, make_variant_item_code
from erpadda.stock.doctype.item.test_item import set_item_variant_settings
from erpadda.stock.doctype.quality_inspection.test_quality_inspection import (
	create_quality_inspection_parameter,
)


class TestItemVariant(unittest.TestCase):
	def test_tables_in_template_copied_to_variant(self):
		fields = [{"field_name": "quality_inspection_template"}]
		set_item_variant_settings(fields)
		variant = make_item_variant()
		self.assertEqual(variant.get("quality_inspection_template"), "_Test QC Template")


def create_variant_with_tables(item, args):
	if isinstance(args, str):
		args = json.loads(args)

	qc_name = make_quality_inspection_template()
	template = vmraid.get_doc("Item", item)
	template.quality_inspection_template = qc_name
	template.save()

	variant = vmraid.new_doc("Item")
	variant.variant_based_on = "Item Attribute"
	variant_attributes = []

	for d in template.attributes:
		variant_attributes.append({"attribute": d.attribute, "attribute_value": args.get(d.attribute)})

	variant.set("attributes", variant_attributes)
	copy_attributes_to_variant(template, variant)
	make_variant_item_code(template.item_code, template.item_name, variant)

	return variant


def make_item_variant():
	vmraid.delete_doc_if_exists("Item", "_Test Variant Item-XSL", force=1)
	variant = create_variant_with_tables("_Test Variant Item", '{"Test Size": "Extra Small"}')
	variant.item_code = "_Test Variant Item-XSL"
	variant.item_name = "_Test Variant Item-XSL"
	variant.save()
	return variant


def make_quality_inspection_template():
	qc_template = "_Test QC Template"
	if vmraid.db.exists("Quality Inspection Template", qc_template):
		return qc_template

	qc = vmraid.new_doc("Quality Inspection Template")
	qc.quality_inspection_template_name = qc_template

	create_quality_inspection_parameter("Moisture")
	qc.append(
		"item_quality_inspection_parameter",
		{
			"specification": "Moisture",
			"value": "&lt; 5%",
		},
	)

	qc.insert()
	return qc.name
