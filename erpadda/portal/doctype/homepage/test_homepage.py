# Copyright (c) 2019, VMRaid and Contributors
# See license.txt

import unittest

import vmraid
from vmraid.utils import set_request
from vmraid.website.serve import get_response


class TestHomepage(unittest.TestCase):
	def test_homepage_load(self):
		set_request(method="GET", path="home")
		response = get_response()

		self.assertEqual(response.status_code, 200)

		html = vmraid.safe_decode(response.get_data())
		self.assertTrue('<section class="hero-section' in html)
