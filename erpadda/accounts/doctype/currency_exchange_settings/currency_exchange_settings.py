# Copyright (c) 2022, VMRaid and contributors
# For license information, please see license.txt

import vmraid
import requests
from vmraid import _
from vmraid.model.document import Document
from vmraid.utils import nowdate


class CurrencyExchangeSettings(Document):
	def validate(self):
		self.set_parameters_and_result()
		if vmraid.flags.in_test or vmraid.flags.in_install or vmraid.flags.in_setup_wizard:
			return
		response, value = self.validate_parameters()
		self.validate_result(response, value)

	def set_parameters_and_result(self):
		if self.service_provider == "exchangerate.host":
			self.set("result_key", [])
			self.set("req_params", [])

			self.api_endpoint = "https://api.exchangerate.host/convert"
			self.append("result_key", {"key": "result"})
			self.append("req_params", {"key": "date", "value": "{transaction_date}"})
			self.append("req_params", {"key": "from", "value": "{from_currency}"})
			self.append("req_params", {"key": "to", "value": "{to_currency}"})
		elif self.service_provider == "frankfurter.app":
			self.set("result_key", [])
			self.set("req_params", [])

			self.api_endpoint = "https://frankfurter.app/{transaction_date}"
			self.append("result_key", {"key": "rates"})
			self.append("result_key", {"key": "{to_currency}"})
			self.append("req_params", {"key": "base", "value": "{from_currency}"})
			self.append("req_params", {"key": "symbols", "value": "{to_currency}"})

	def validate_parameters(self):
		params = {}
		for row in self.req_params:
			params[row.key] = row.value.format(
				transaction_date=nowdate(), to_currency="INR", from_currency="USD"
			)

		api_url = self.api_endpoint.format(
			transaction_date=nowdate(), to_currency="INR", from_currency="USD"
		)

		try:
			response = requests.get(api_url, params=params)
		except requests.exceptions.RequestException as e:
			vmraid.throw("Error: " + str(e))

		response.raise_for_status()
		value = response.json()

		return response, value

	def validate_result(self, response, value):
		try:
			for key in self.result_key:
				value = value[
					str(key.key).format(transaction_date=nowdate(), to_currency="INR", from_currency="USD")
				]
		except Exception:
			vmraid.throw(_("Invalid result key. Response:") + " " + response.text)
		if not isinstance(value, (int, float)):
			vmraid.throw(_("Returned exchange rate is neither integer not float."))

		self.url = response.url
