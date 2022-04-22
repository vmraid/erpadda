# -*- coding: utf-8 -*-
# Copyright (c) 2021, VMRaid and contributors
# For license information, please see license.txt

import json

import vmraid
from vmraid import _
from vmraid.utils import cint, cstr, flt, random_string
from vmraid.website.doctype.website_slideshow.website_slideshow import get_slideshow
from vmraid.website.website_generator import WebsiteGenerator

from erpadda.e_commerce.doctype.item_review.item_review import get_item_reviews
from erpadda.e_commerce.redisearch_utils import (
	delete_item_from_index,
	insert_item_to_index,
	update_index_for_item,
)
from erpadda.e_commerce.shopping_cart.cart import _set_price_list
from erpadda.setup.doctype.item_group.item_group import (
	get_parent_item_groups,
	invalidate_cache_for,
)
from erpadda.utilities.product import get_price


class WebsiteItem(WebsiteGenerator):
	website = vmraid._dict(
		page_title_field="web_item_name",
		condition_field="published",
		template="templates/generators/item/item.html",
		no_cache=1,
	)

	def autoname(self):
		# use naming series to accomodate items with same name (different item code)
		from vmraid.model.naming import make_autoname

		from erpadda.setup.doctype.naming_series.naming_series import get_default_naming_series

		naming_series = get_default_naming_series("Website Item")
		if not self.name and naming_series:
			self.name = make_autoname(naming_series, doc=self)

	def onload(self):
		super(WebsiteItem, self).onload()

	def validate(self):
		super(WebsiteItem, self).validate()

		if not self.item_code:
			vmraid.throw(_("Item Code is required"), title=_("Mandatory"))

		self.validate_duplicate_website_item()
		self.validate_website_image()
		self.make_thumbnail()
		self.publish_unpublish_desk_item(publish=True)

		if not self.get("__islocal"):
			wig = vmraid.qb.DocType("Website Item Group")
			query = (
				vmraid.qb.from_(wig)
				.select(wig.item_group)
				.where(
					(wig.parentfield == "website_item_groups")
					& (wig.parenttype == "Website Item")
					& (wig.parent == self.name)
				)
			)
			result = query.run(as_list=True)

			self.old_website_item_groups = [x[0] for x in result]

	def on_update(self):
		invalidate_cache_for_web_item(self)
		self.update_template_item()

	def on_trash(self):
		super(WebsiteItem, self).on_trash()
		delete_item_from_index(self)
		self.publish_unpublish_desk_item(publish=False)

	def validate_duplicate_website_item(self):
		existing_web_item = vmraid.db.exists("Website Item", {"item_code": self.item_code})
		if existing_web_item and existing_web_item != self.name:
			message = _("Website Item already exists against Item {0}").format(vmraid.bold(self.item_code))
			vmraid.throw(message, title=_("Already Published"))

	def publish_unpublish_desk_item(self, publish=True):
		if vmraid.db.get_value("Item", self.item_code, "published_in_website") and publish:
			return  # if already published don't publish again
		vmraid.db.set_value("Item", self.item_code, "published_in_website", publish)

	def make_route(self):
		"""Called from set_route in WebsiteGenerator."""
		if not self.route:
			return (
				cstr(vmraid.db.get_value("Item Group", self.item_group, "route"))
				+ "/"
				+ self.scrub((self.item_name if self.item_name else self.item_code) + "-" + random_string(5))
			)

	def update_template_item(self):
		"""Publish Template Item if Variant is published."""
		if self.variant_of:
			if self.published:
				# show template
				template_item = vmraid.get_doc("Item", self.variant_of)

				if not template_item.published_in_website:
					template_item.flags.ignore_permissions = True
					make_website_item(template_item)

	def validate_website_image(self):
		if vmraid.flags.in_import:
			return

		"""Validate if the website image is a public file"""
		auto_set_website_image = False
		if not self.website_image and self.image:
			auto_set_website_image = True
			self.website_image = self.image

		if not self.website_image:
			return

		# find if website image url exists as public
		file_doc = vmraid.get_all(
			"File",
			filters={"file_url": self.website_image},
			fields=["name", "is_private"],
			order_by="is_private asc",
			limit_page_length=1,
		)

		if file_doc:
			file_doc = file_doc[0]

		if not file_doc:
			if not auto_set_website_image:
				vmraid.msgprint(
					_("Website Image {0} attached to Item {1} cannot be found").format(
						self.website_image, self.name
					)
				)

			self.website_image = None

		elif file_doc.is_private:
			if not auto_set_website_image:
				vmraid.msgprint(_("Website Image should be a public file or website URL"))

			self.website_image = None

	def make_thumbnail(self):
		"""Make a thumbnail of `website_image`"""
		if vmraid.flags.in_import or vmraid.flags.in_migrate:
			return

		import requests.exceptions

		if not self.is_new() and self.website_image != vmraid.db.get_value(
			self.doctype, self.name, "website_image"
		):
			self.thumbnail = None

		if self.website_image and not self.thumbnail:
			file_doc = None

			try:
				file_doc = vmraid.get_doc(
					"File",
					{
						"file_url": self.website_image,
						"attached_to_doctype": "Website Item",
						"attached_to_name": self.name,
					},
				)
			except vmraid.DoesNotExistError:
				pass
				# cleanup
				vmraid.local.message_log.pop()

			except requests.exceptions.HTTPError:
				vmraid.msgprint(_("Warning: Invalid attachment {0}").format(self.website_image))
				self.website_image = None

			except requests.exceptions.SSLError:
				vmraid.msgprint(
					_("Warning: Invalid SSL certificate on attachment {0}").format(self.website_image)
				)
				self.website_image = None

			# for CSV import
			if self.website_image and not file_doc:
				try:
					file_doc = vmraid.get_doc(
						{
							"doctype": "File",
							"file_url": self.website_image,
							"attached_to_doctype": "Website Item",
							"attached_to_name": self.name,
						}
					).save()

				except IOError:
					self.website_image = None

			if file_doc:
				if not file_doc.thumbnail_url:
					file_doc.make_thumbnail()

				self.thumbnail = file_doc.thumbnail_url

	def get_context(self, context):
		context.show_search = True
		context.search_link = "/search"
		context.body_class = "product-page"

		context.parents = get_parent_item_groups(self.item_group, from_item=True)  # breadcumbs
		self.attributes = vmraid.get_all(
			"Item Variant Attribute",
			fields=["attribute", "attribute_value"],
			filters={"parent": self.item_code},
		)

		if self.slideshow:
			context.update(get_slideshow(self))

		self.set_metatags(context)
		self.set_shopping_cart_data(context)

		settings = context.shopping_cart.cart_settings

		self.get_product_details_section(context)

		if settings.get("enable_reviews"):
			reviews_data = get_item_reviews(self.name)
			context.update(reviews_data)
			context.reviews = context.reviews[:4]

		context.wished = False
		if vmraid.db.exists(
			"Wishlist Item", {"item_code": self.item_code, "parent": vmraid.session.user}
		):
			context.wished = True

		context.user_is_customer = check_if_user_is_customer()

		context.recommended_items = None
		if settings and settings.enable_recommendations:
			context.recommended_items = self.get_recommended_items(settings)

		return context

	def set_selected_attributes(self, variants, context, attribute_values_available):
		for variant in variants:
			variant.attributes = vmraid.get_all(
				"Item Variant Attribute",
				filters={"parent": variant.name},
				fields=["attribute", "attribute_value as value"],
			)

			# make an attribute-value map for easier access in templates
			variant.attribute_map = vmraid._dict(
				{attr.attribute: attr.value for attr in variant.attributes}
			)

			for attr in variant.attributes:
				values = attribute_values_available.setdefault(attr.attribute, [])
				if attr.value not in values:
					values.append(attr.value)

				if variant.name == context.variant.name:
					context.selected_attributes[attr.attribute] = attr.value

	def set_attribute_values(self, attributes, context, attribute_values_available):
		for attr in attributes:
			values = context.attribute_values.setdefault(attr.attribute, [])

			if cint(vmraid.db.get_value("Item Attribute", attr.attribute, "numeric_values")):
				for val in sorted(attribute_values_available.get(attr.attribute, []), key=flt):
					values.append(val)
			else:
				# get list of values defined (for sequence)
				for attr_value in vmraid.db.get_all(
					"Item Attribute Value",
					fields=["attribute_value"],
					filters={"parent": attr.attribute},
					order_by="idx asc",
				):

					if attr_value.attribute_value in attribute_values_available.get(attr.attribute, []):
						values.append(attr_value.attribute_value)

	def set_metatags(self, context):
		context.metatags = vmraid._dict({})

		safe_description = vmraid.utils.to_markdown(self.description)

		context.metatags.url = vmraid.utils.get_url() + "/" + context.route

		if context.website_image:
			if context.website_image.startswith("http"):
				url = context.website_image
			else:
				url = vmraid.utils.get_url() + context.website_image
			context.metatags.image = url

		context.metatags.description = safe_description[:300]

		context.metatags.title = self.web_item_name or self.item_name or self.item_code

		context.metatags["og:type"] = "product"
		context.metatags["og:site_name"] = "ERPAdda"

	def set_shopping_cart_data(self, context):
		from erpadda.e_commerce.shopping_cart.product_info import get_product_info_for_website

		context.shopping_cart = get_product_info_for_website(
			self.item_code, skip_quotation_creation=True
		)

	def copy_specification_from_item_group(self):
		self.set("website_specifications", [])
		if self.item_group:
			for label, desc in vmraid.db.get_values(
				"Item Website Specification", {"parent": self.item_group}, ["label", "description"]
			):
				row = self.append("website_specifications")
				row.label = label
				row.description = desc

	def get_product_details_section(self, context):
		"""Get section with tabs or website specifications."""
		context.show_tabs = self.show_tabbed_section
		if self.show_tabbed_section and (self.tabs or self.website_specifications):
			context.tabs = self.get_tabs()
		else:
			context.website_specifications = self.website_specifications

	def get_tabs(self):
		tab_values = {}
		tab_values["tab_1_title"] = "Product Details"
		tab_values["tab_1_content"] = vmraid.render_template(
			"templates/generators/item/item_specifications.html",
			{"website_specifications": self.website_specifications, "show_tabs": self.show_tabbed_section},
		)

		for row in self.tabs:
			tab_values[f"tab_{row.idx + 1}_title"] = _(row.label)
			tab_values[f"tab_{row.idx + 1}_content"] = row.content

		return tab_values

	def get_recommended_items(self, settings):
		ri = vmraid.qb.DocType("Recommended Items")
		wi = vmraid.qb.DocType("Website Item")

		query = (
			vmraid.qb.from_(ri)
			.join(wi)
			.on(ri.item_code == wi.item_code)
			.select(ri.item_code, ri.route, ri.website_item_name, ri.website_item_thumbnail)
			.where((ri.parent == self.name) & (wi.published == 1))
			.orderby(ri.idx)
		)
		items = query.run(as_dict=True)

		if settings.show_price:
			is_guest = vmraid.session.user == "Guest"
			# Show Price if logged in.
			# If not logged in and price is hidden for guest, skip price fetch.
			if is_guest and settings.hide_price_for_guest:
				return items

			selling_price_list = _set_price_list(settings, None)
			for item in items:
				item.price_info = get_price(
					item.item_code, selling_price_list, settings.default_customer_group, settings.company
				)

		return items


def invalidate_cache_for_web_item(doc):
	"""Invalidate Website Item Group cache and rebuild ItemVariantsCacheManager."""
	from erpadda.stock.doctype.item.item import invalidate_item_variants_cache_for_website

	invalidate_cache_for(doc, doc.item_group)

	website_item_groups = list(
		set(
			(doc.get("old_website_item_groups") or [])
			+ [d.item_group for d in doc.get({"doctype": "Website Item Group"}) if d.item_group]
		)
	)

	for item_group in website_item_groups:
		invalidate_cache_for(doc, item_group)

	# Update Search Cache
	update_index_for_item(doc)

	invalidate_item_variants_cache_for_website(doc)


def on_doctype_update():
	# since route is a Text column, it needs a length for indexing
	vmraid.db.add_index("Website Item", ["route(500)"])

	vmraid.db.add_index("Website Item", ["item_group"])
	vmraid.db.add_index("Website Item", ["brand"])


def check_if_user_is_customer(user=None):
	from vmraid.contacts.doctype.contact.contact import get_contact_name

	if not user:
		user = vmraid.session.user

	contact_name = get_contact_name(user)
	customer = None

	if contact_name:
		contact = vmraid.get_doc("Contact", contact_name)
		for link in contact.links:
			if link.link_doctype == "Customer":
				customer = link.link_name
				break

	return True if customer else False


@vmraid.whitelist()
def make_website_item(doc, save=True):
	if not doc:
		return

	if isinstance(doc, str):
		doc = json.loads(doc)

	if vmraid.db.exists("Website Item", {"item_code": doc.get("item_code")}):
		message = _("Website Item already exists against {0}").format(vmraid.bold(doc.get("item_code")))
		vmraid.throw(message, title=_("Already Published"))

	website_item = vmraid.new_doc("Website Item")
	website_item.web_item_name = doc.get("item_name")

	fields_to_map = [
		"item_code",
		"item_name",
		"item_group",
		"stock_uom",
		"brand",
		"image",
		"has_variants",
		"variant_of",
		"description",
	]
	for field in fields_to_map:
		website_item.update({field: doc.get(field)})

	if not save:
		return website_item

	website_item.save()

	# Add to search cache
	insert_item_to_index(website_item)

	return [website_item.name, website_item.web_item_name]
