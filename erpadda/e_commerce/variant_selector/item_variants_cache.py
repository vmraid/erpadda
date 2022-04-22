import vmraid


class ItemVariantsCacheManager:
	def __init__(self, item_code):
		self.item_code = item_code

	def get_item_variants_data(self):
		val = vmraid.cache().hget("item_variants_data", self.item_code)

		if not val:
			self.build_cache()

		return vmraid.cache().hget("item_variants_data", self.item_code)

	def get_attribute_value_item_map(self):
		val = vmraid.cache().hget("attribute_value_item_map", self.item_code)

		if not val:
			self.build_cache()

		return vmraid.cache().hget("attribute_value_item_map", self.item_code)

	def get_item_attribute_value_map(self):
		val = vmraid.cache().hget("item_attribute_value_map", self.item_code)

		if not val:
			self.build_cache()

		return vmraid.cache().hget("item_attribute_value_map", self.item_code)

	def get_optional_attributes(self):
		val = vmraid.cache().hget("optional_attributes", self.item_code)

		if not val:
			self.build_cache()

		return vmraid.cache().hget("optional_attributes", self.item_code)

	def get_ordered_attribute_values(self):
		val = vmraid.cache().get_value("ordered_attribute_values_map")
		if val:
			return val

		all_attribute_values = vmraid.get_all(
			"Item Attribute Value", ["attribute_value", "idx", "parent"], order_by="idx asc"
		)

		ordered_attribute_values_map = vmraid._dict({})
		for d in all_attribute_values:
			ordered_attribute_values_map.setdefault(d.parent, []).append(d.attribute_value)

		vmraid.cache().set_value("ordered_attribute_values_map", ordered_attribute_values_map)
		return ordered_attribute_values_map

	def build_cache(self):
		parent_item_code = self.item_code

		attributes = [
			a.attribute
			for a in vmraid.get_all(
				"Item Variant Attribute", {"parent": parent_item_code}, ["attribute"], order_by="idx asc"
			)
		]

		# Get Variants and tehir Attributes that are not disabled
		iva = vmraid.qb.DocType("Item Variant Attribute")
		item = vmraid.qb.DocType("Item")
		query = (
			vmraid.qb.from_(iva)
			.join(item)
			.on(item.name == iva.parent)
			.select(iva.parent, iva.attribute, iva.attribute_value)
			.where((iva.variant_of == parent_item_code) & (item.disabled == 0))
			.orderby(iva.name)
		)
		item_variants_data = query.run()

		attribute_value_item_map = vmraid._dict()
		item_attribute_value_map = vmraid._dict()

		for row in item_variants_data:
			item_code, attribute, attribute_value = row
			# (attr, value) => [item1, item2]
			attribute_value_item_map.setdefault((attribute, attribute_value), []).append(item_code)
			# item => {attr1: value1, attr2: value2}
			item_attribute_value_map.setdefault(item_code, {})[attribute] = attribute_value

		optional_attributes = set()
		for item_code, attr_dict in item_attribute_value_map.items():
			for attribute in attributes:
				if attribute not in attr_dict:
					optional_attributes.add(attribute)

		vmraid.cache().hset("attribute_value_item_map", parent_item_code, attribute_value_item_map)
		vmraid.cache().hset("item_attribute_value_map", parent_item_code, item_attribute_value_map)
		vmraid.cache().hset("item_variants_data", parent_item_code, item_variants_data)
		vmraid.cache().hset("optional_attributes", parent_item_code, optional_attributes)

	def clear_cache(self):
		keys = [
			"attribute_value_item_map",
			"item_attribute_value_map",
			"item_variants_data",
			"optional_attributes",
		]

		for key in keys:
			vmraid.cache().hdel(key, self.item_code)

	def rebuild_cache(self):
		self.clear_cache()
		enqueue_build_cache(self.item_code)


def build_cache(item_code):
	vmraid.cache().hset("item_cache_build_in_progress", item_code, 1)
	i = ItemVariantsCacheManager(item_code)
	i.build_cache()
	vmraid.cache().hset("item_cache_build_in_progress", item_code, 0)


def enqueue_build_cache(item_code):
	if vmraid.cache().hget("item_cache_build_in_progress", item_code):
		return
	vmraid.enqueue(
		"erpadda.e_commerce.variant_selector.item_variants_cache.build_cache",
		item_code=item_code,
		queue="long",
	)
