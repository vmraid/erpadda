# Copyright (c) 2017, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid

parentfield = {"item_code": "items", "item_group": "item_groups", "brand": "brands"}


def execute():

	if not vmraid.get_all("Pricing Rule", limit=1):
		return

	vmraid.reload_doc("accounts", "doctype", "pricing_rule_detail")
	doctypes = {
		"Supplier Quotation": "buying",
		"Purchase Order": "buying",
		"Purchase Invoice": "accounts",
		"Purchase Receipt": "stock",
		"Quotation": "selling",
		"Sales Order": "selling",
		"Sales Invoice": "accounts",
		"Delivery Note": "stock",
	}

	for doctype, module in doctypes.items():
		vmraid.reload_doc(module, "doctype", vmraid.scrub(doctype))

		child_doc = vmraid.scrub(doctype) + "_item"
		vmraid.reload_doc(module, "doctype", child_doc, force=True)

		child_doctype = doctype + " Item"

		vmraid.db.sql(
			""" UPDATE `tab{child_doctype}` SET pricing_rules = pricing_rule
			WHERE docstatus < 2 and pricing_rule is not null and pricing_rule != ''
		""".format(
				child_doctype=child_doctype
			)
		)

		data = vmraid.db.sql(
			""" SELECT pricing_rule, name, parent,
				parenttype, creation, modified, docstatus, modified_by, owner, name
			FROM `tab{child_doc}` where docstatus < 2 and pricing_rule is not null
			and pricing_rule != ''""".format(
				child_doc=child_doctype
			),
			as_dict=1,
		)

		values = []
		for d in data:
			values.append(
				(
					d.pricing_rule,
					d.name,
					d.parent,
					"pricing_rules",
					d.parenttype,
					d.creation,
					d.modified,
					d.docstatus,
					d.modified_by,
					d.owner,
					vmraid.generate_hash("", 10),
				)
			)

		if values:
			vmraid.db.sql(
				""" INSERT INTO
				`tabPricing Rule Detail` (`pricing_rule`, `child_docname`, `parent`, `parentfield`, `parenttype`,
				`creation`, `modified`, `docstatus`, `modified_by`, `owner`, `name`)
			VALUES {values} """.format(
					values=", ".join(["%s"] * len(values))
				),
				tuple(values),
			)

	vmraid.reload_doc("accounts", "doctype", "pricing_rule")

	for doctype, apply_on in {
		"Pricing Rule Item Code": "Item Code",
		"Pricing Rule Item Group": "Item Group",
		"Pricing Rule Brand": "Brand",
	}.items():
		vmraid.reload_doc("accounts", "doctype", vmraid.scrub(doctype))

		field = vmraid.scrub(apply_on)
		data = vmraid.get_all(
			"Pricing Rule",
			fields=[field, "name", "creation", "modified", "owner", "modified_by"],
			filters={"apply_on": apply_on},
		)

		values = []
		for d in data:
			values.append(
				(
					d.get(field),
					d.name,
					parentfield.get(field),
					"Pricing Rule",
					d.creation,
					d.modified,
					d.owner,
					d.modified_by,
					vmraid.generate_hash("", 10),
				)
			)

		if values:
			vmraid.db.sql(
				""" INSERT INTO
				`tab{doctype}` ({field}, parent, parentfield, parenttype, creation, modified,
					owner, modified_by, name)
			VALUES {values} """.format(
					doctype=doctype, field=field, values=", ".join(["%s"] * len(values))
				),
				tuple(values),
			)
