# Copyright (c) 2019, VMRaid and contributors
# For license information, please see license.txt


import vmraid
import requests
from vmraid import _
from vmraid.model.document import Document


class ExotelSettings(Document):
	def validate(self):
		self.verify_credentials()

	def verify_credentials(self):
		if self.enabled:
			response = requests.get(
				"https://api.exotel.com/v1/Accounts/{sid}".format(sid=self.account_sid),
				auth=(self.api_key, self.api_token),
			)
			if response.status_code != 200:
				vmraid.throw(_("Invalid credentials"))
