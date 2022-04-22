import vmraid


def execute():
	vmraid.reload_doc("stock", "doctype", "item_variant_attribute")
	vmraid.db.sql(
		"""
		UPDATE `tabItem Variant Attribute` t1
		INNER JOIN `tabItem` t2 ON t2.name = t1.parent
		SET t1.variant_of = t2.variant_of
	"""
	)
