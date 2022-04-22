# Copyright (c) 2018, VMRaid and contributors
# For license information, please see license.txt


import vmraid
from vmraid.model.document import Document


class QualityInspectionTemplate(Document):
	pass


def get_template_details(template):
	if not template:
		return []

	return vmraid.get_all(
		"Item Quality Inspection Parameter",
		fields=[
			"specification",
			"value",
			"acceptance_formula",
			"numeric",
			"formula_based_criteria",
			"min_value",
			"max_value",
		],
		filters={"parenttype": "Quality Inspection Template", "parent": template},
		order_by="idx",
	)
