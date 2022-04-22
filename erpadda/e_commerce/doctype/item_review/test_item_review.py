# -*- coding: utf-8 -*-
# Copyright (c) 2021, VMRaid and Contributors
# See license.txt
import unittest

import vmraid
from vmraid.core.doctype.user_permission.test_user_permission import create_user

from erpadda.e_commerce.doctype.e_commerce_settings.test_e_commerce_settings import (
	setup_e_commerce_settings,
)
from erpadda.e_commerce.doctype.item_review.item_review import (
	UnverifiedReviewer,
	add_item_review,
	get_item_reviews,
)
from erpadda.e_commerce.doctype.website_item.website_item import make_website_item
from erpadda.e_commerce.shopping_cart.cart import get_party
from erpadda.stock.doctype.item.test_item import make_item


class TestItemReview(unittest.TestCase):
	def setUp(self):
		item = make_item("Test Mobile Phone")
		if not vmraid.db.exists("Website Item", {"item_code": "Test Mobile Phone"}):
			make_website_item(item, save=True)

		setup_e_commerce_settings({"enable_reviews": 1})
		vmraid.local.shopping_cart_settings = None

	def tearDown(self):
		vmraid.get_cached_doc("Website Item", {"item_code": "Test Mobile Phone"}).delete()
		setup_e_commerce_settings({"enable_reviews": 0})

	def test_add_and_get_item_reviews_from_customer(self):
		"Add / Get Reviews from a User that is a valid customer (has added to cart or purchased in the past)"
		# create user
		web_item = vmraid.db.get_value("Website Item", {"item_code": "Test Mobile Phone"})
		test_user = create_user("test_reviewer@example.com", "Customer")
		vmraid.set_user(test_user.name)

		# create customer and contact against user
		customer = get_party()

		# post review on "Test Mobile Phone"
		try:
			add_item_review(web_item, "Great Product", 3, "Would recommend this product")
			review_name = vmraid.db.get_value("Item Review", {"website_item": web_item})
		except Exception:
			self.fail(f"Error while publishing review for {web_item}")

		review_data = get_item_reviews(web_item, 0, 10)

		self.assertEqual(len(review_data.reviews), 1)
		self.assertEqual(review_data.average_rating, 3)
		self.assertEqual(review_data.reviews_per_rating[2], 100)

		# tear down
		vmraid.set_user("Administrator")
		vmraid.delete_doc("Item Review", review_name)
		customer.delete()

	def test_add_item_review_from_non_customer(self):
		"Check if logged in user (who is not a customer yet) is blocked from posting reviews."
		web_item = vmraid.db.get_value("Website Item", {"item_code": "Test Mobile Phone"})
		test_user = create_user("test_reviewer@example.com", "Customer")
		vmraid.set_user(test_user.name)

		with self.assertRaises(UnverifiedReviewer):
			add_item_review(web_item, "Great Product", 3, "Would recommend this product")

		# tear down
		vmraid.set_user("Administrator")

	def test_add_item_reviews_from_guest_user(self):
		"Check if Guest user is blocked from posting reviews."
		web_item = vmraid.db.get_value("Website Item", {"item_code": "Test Mobile Phone"})
		vmraid.set_user("Guest")

		with self.assertRaises(UnverifiedReviewer):
			add_item_review(web_item, "Great Product", 3, "Would recommend this product")

		# tear down
		vmraid.set_user("Administrator")
