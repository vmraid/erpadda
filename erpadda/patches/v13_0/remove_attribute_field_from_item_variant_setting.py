import vmraid


def execute():
	"""Remove has_variants and attribute fields from item variant settings."""
	vmraid.reload_doc("stock", "doctype", "Item Variant Settings")

	vmraid.db.sql(
		"""delete from `tabVariant Field`
			where field_name in ('attributes', 'has_variants')"""
	)
