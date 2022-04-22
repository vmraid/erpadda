# Copyright (c) 2018, VMRaid and contributors
# For license information, please see license.txt


import json

import vmraid
from vmraid.model.document import Document
from vmraid.utils.jinja import validate_template


class ContractTemplate(Document):
	def validate(self):
		if self.contract_terms:
			validate_template(self.contract_terms)


@vmraid.whitelist()
def get_contract_template(template_name, doc):
	if isinstance(doc, str):
		doc = json.loads(doc)

	contract_template = vmraid.get_doc("Contract Template", template_name)
	contract_terms = None

	if contract_template.contract_terms:
		contract_terms = vmraid.render_template(contract_template.contract_terms, doc)

	return {"contract_template": contract_template, "contract_terms": contract_terms}
