""" smoak tests to check basic functionality calls on known form loads."""

import vmraid
from vmraid.desk.form.load import getdoc
from vmraid.tests.utils import VMRaidTestCase, change_settings
from vmraid.www.printview import get_html_and_style


class TestFormLoads(VMRaidTestCase):
	@change_settings("Print Settings", {"allow_print_for_cancelled": 1})
	def test_load(self):
		erpadda_modules = vmraid.get_all("Module Def", filters={"app_name": "erpadda"}, pluck="name")
		doctypes = vmraid.get_all(
			"DocType",
			{"istable": 0, "issingle": 0, "is_virtual": 0, "module": ("in", erpadda_modules)},
			pluck="name",
		)

		for doctype in doctypes:
			last_doc = vmraid.db.get_value(doctype, {}, "name", order_by="modified desc")
			if not last_doc:
				continue
			with self.subTest(msg=f"Loading {doctype} - {last_doc}", doctype=doctype, last_doc=last_doc):
				self.assertFormLoad(doctype, last_doc)
				self.assertDocPrint(doctype, last_doc)

	def assertFormLoad(self, doctype, docname):
		# reset previous response
		vmraid.response = vmraid._dict({"docs": []})
		vmraid.response.docinfo = None

		try:
			getdoc(doctype, docname)
		except Exception as e:
			self.fail(f"Failed to load {doctype}-{docname}: {e}")

		self.assertTrue(
			vmraid.response.docs, msg=f"expected document in reponse, found: {vmraid.response.docs}"
		)
		self.assertTrue(
			vmraid.response.docinfo, msg=f"expected docinfo in reponse, found: {vmraid.response.docinfo}"
		)

	def assertDocPrint(self, doctype, docname):
		doc = vmraid.get_doc(doctype, docname)
		doc.set("__onload", vmraid._dict())
		doc.run_method("onload")

		messages_before = vmraid.get_message_log()
		ret = get_html_and_style(doc=doc.as_json(), print_format="Standard", no_letterhead=1)
		messages_after = vmraid.get_message_log()

		if len(messages_after) > len(messages_before):
			new_messages = messages_after[len(messages_before) :]
			self.fail("Print view showing error/warnings: \n" + "\n".join(str(msg) for msg in new_messages))

		# html should exist
		self.assertTrue(bool(ret["html"]))
