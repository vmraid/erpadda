# Copyright (c) 2015, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid

no_cache = 1


def get_context(context):
	homepage = vmraid.get_cached_doc("Homepage")

	for item in homepage.products:
		route = vmraid.db.get_value("Website Item", {"item_code": item.item_code}, "route")
		if route:
			item.route = "/" + route

	homepage.title = homepage.title or homepage.company
	context.title = homepage.title
	context.homepage = homepage

	if homepage.hero_section_based_on == "Homepage Section" and homepage.hero_section:
		homepage.hero_section_doc = vmraid.get_cached_doc("Homepage Section", homepage.hero_section)

	if homepage.slideshow:
		doc = vmraid.get_cached_doc("Website Slideshow", homepage.slideshow)
		context.slideshow = homepage.slideshow
		context.slideshow_header = doc.header
		context.slides = doc.slideshow_items

	context.blogs = vmraid.get_all(
		"Blog Post",
		fields=["title", "blogger", "blog_intro", "route"],
		filters={"published": 1},
		order_by="modified desc",
		limit=3,
	)

	# filter out homepage section which is used as hero section
	homepage_hero_section = (
		homepage.hero_section_based_on == "Homepage Section" and homepage.hero_section
	)
	homepage_sections = vmraid.get_all(
		"Homepage Section",
		filters=[["name", "!=", homepage_hero_section]] if homepage_hero_section else None,
		order_by="section_order asc",
	)
	context.homepage_sections = [
		vmraid.get_cached_doc("Homepage Section", name) for name in homepage_sections
	]

	context.metatags = context.metatags or vmraid._dict({})
	context.metatags.image = homepage.hero_image or None
	context.metatags.description = homepage.description or None

	context.explore_link = "/all-products"
