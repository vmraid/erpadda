# -*- coding: utf-8 -*-
# Copyright (c) 2021, VMRaid and Contributors
# See license.txt
import unittest

import vmraid
from vmraid.core.doctype.user_permission.test_user_permission import create_user

from erpadda.e_commerce.doctype.website_item.website_item import make_website_item
from erpadda.e_commerce.doctype.wishlist.wishlist import add_to_wishlist, remove_from_wishlist
from erpadda.stock.doctype.item.test_item import make_item


class TestWishlist(unittest.TestCase):
	def setUp(self):
		item = make_item("Test Phone Series X")
		if not vmraid.db.exists("Website Item", {"item_code": "Test Phone Series X"}):
			make_website_item(item, save=True)

		item = make_item("Test Phone Series Y")
		if not vmraid.db.exists("Website Item", {"item_code": "Test Phone Series Y"}):
			make_website_item(item, save=True)

	def tearDown(self):
		vmraid.get_cached_doc("Website Item", {"item_code": "Test Phone Series X"}).delete()
		vmraid.get_cached_doc("Website Item", {"item_code": "Test Phone Series Y"}).delete()
		vmraid.get_cached_doc("Item", "Test Phone Series X").delete()
		vmraid.get_cached_doc("Item", "Test Phone Series Y").delete()

	def test_add_remove_items_in_wishlist(self):
		"Check if items are added and removed from user's wishlist."
		# add first item
		add_to_wishlist("Test Phone Series X")

		# check if wishlist was created and item was added
		self.assertTrue(vmraid.db.exists("Wishlist", {"user": vmraid.session.user}))
		self.assertTrue(
			vmraid.db.exists(
				"Wishlist Item", {"item_code": "Test Phone Series X", "parent": vmraid.session.user}
			)
		)

		# add second item to wishlist
		add_to_wishlist("Test Phone Series Y")
		wishlist_length = vmraid.db.get_value(
			"Wishlist Item", {"parent": vmraid.session.user}, "count(*)"
		)
		self.assertEqual(wishlist_length, 2)

		remove_from_wishlist("Test Phone Series X")
		remove_from_wishlist("Test Phone Series Y")

		wishlist_length = vmraid.db.get_value(
			"Wishlist Item", {"parent": vmraid.session.user}, "count(*)"
		)
		self.assertIsNone(vmraid.db.exists("Wishlist Item", {"parent": vmraid.session.user}))
		self.assertEqual(wishlist_length, 0)

		# tear down
		vmraid.get_doc("Wishlist", {"user": vmraid.session.user}).delete()

	def test_add_remove_in_wishlist_multiple_users(self):
		"Check if items are added and removed from the correct user's wishlist."
		test_user = create_user("test_reviewer@example.com", "Customer")
		test_user_1 = create_user("test_reviewer_1@example.com", "Customer")

		# add to wishlist for first user
		vmraid.set_user(test_user.name)
		add_to_wishlist("Test Phone Series X")

		# add to wishlist for second user
		vmraid.set_user(test_user_1.name)
		add_to_wishlist("Test Phone Series X")

		# check wishlist and its content for users
		self.assertTrue(vmraid.db.exists("Wishlist", {"user": test_user.name}))
		self.assertTrue(
			vmraid.db.exists(
				"Wishlist Item", {"item_code": "Test Phone Series X", "parent": test_user.name}
			)
		)

		self.assertTrue(vmraid.db.exists("Wishlist", {"user": test_user_1.name}))
		self.assertTrue(
			vmraid.db.exists(
				"Wishlist Item", {"item_code": "Test Phone Series X", "parent": test_user_1.name}
			)
		)

		# remove item for second user
		remove_from_wishlist("Test Phone Series X")

		# make sure item was removed for second user and not first
		self.assertFalse(
			vmraid.db.exists(
				"Wishlist Item", {"item_code": "Test Phone Series X", "parent": test_user_1.name}
			)
		)
		self.assertTrue(
			vmraid.db.exists(
				"Wishlist Item", {"item_code": "Test Phone Series X", "parent": test_user.name}
			)
		)

		# remove item for first user
		vmraid.set_user(test_user.name)
		remove_from_wishlist("Test Phone Series X")
		self.assertFalse(
			vmraid.db.exists(
				"Wishlist Item", {"item_code": "Test Phone Series X", "parent": test_user.name}
			)
		)

		# tear down
		vmraid.set_user("Administrator")
		vmraid.get_doc("Wishlist", {"user": test_user.name}).delete()
		vmraid.get_doc("Wishlist", {"user": test_user_1.name}).delete()
