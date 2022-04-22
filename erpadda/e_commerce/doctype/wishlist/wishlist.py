# -*- coding: utf-8 -*-
# Copyright (c) 2021, VMRaid and contributors
# For license information, please see license.txt

import vmraid
from vmraid.model.document import Document


class Wishlist(Document):
	pass


@vmraid.whitelist()
def add_to_wishlist(item_code):
	"""Insert Item into wishlist."""

	if vmraid.db.exists("Wishlist Item", {"item_code": item_code, "parent": vmraid.session.user}):
		return

	web_item_data = vmraid.db.get_value(
		"Website Item",
		{"item_code": item_code},
		["image", "website_warehouse", "name", "web_item_name", "item_name", "item_group", "route"],
		as_dict=1,
	)

	wished_item_dict = {
		"item_code": item_code,
		"item_name": web_item_data.get("item_name"),
		"item_group": web_item_data.get("item_group"),
		"website_item": web_item_data.get("name"),
		"web_item_name": web_item_data.get("web_item_name"),
		"image": web_item_data.get("image"),
		"warehouse": web_item_data.get("website_warehouse"),
		"route": web_item_data.get("route"),
	}

	if not vmraid.db.exists("Wishlist", vmraid.session.user):
		# initialise wishlist
		wishlist = vmraid.get_doc({"doctype": "Wishlist"})
		wishlist.user = vmraid.session.user
		wishlist.append("items", wished_item_dict)
		wishlist.save(ignore_permissions=True)
	else:
		wishlist = vmraid.get_doc("Wishlist", vmraid.session.user)
		item = wishlist.append("items", wished_item_dict)
		item.db_insert()

	if hasattr(vmraid.local, "cookie_manager"):
		vmraid.local.cookie_manager.set_cookie("wish_count", str(len(wishlist.items)))


@vmraid.whitelist()
def remove_from_wishlist(item_code):
	if vmraid.db.exists("Wishlist Item", {"item_code": item_code, "parent": vmraid.session.user}):
		vmraid.db.delete("Wishlist Item", {"item_code": item_code, "parent": vmraid.session.user})
		vmraid.db.commit()  # nosemgrep

		wishlist_items = vmraid.db.get_values("Wishlist Item", filters={"parent": vmraid.session.user})

		if hasattr(vmraid.local, "cookie_manager"):
			vmraid.local.cookie_manager.set_cookie("wish_count", str(len(wishlist_items)))
