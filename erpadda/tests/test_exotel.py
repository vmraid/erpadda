import vmraid
from vmraid.contacts.doctype.contact.test_contact import create_contact
from vmraid.tests.test_api import VMRaidAPITestCase

from erpadda.hr.doctype.employee.test_employee import make_employee


class TestExotel(VMRaidAPITestCase):
	@classmethod
	def setUpClass(cls):
		cls.CURRENT_DB_CONNECTION = vmraid.db
		cls.test_employee_name = make_employee(
			user="test_employee_exotel@company.com", cell_number="9999999999"
		)
		vmraid.db.set_value("Exotel Settings", "Exotel Settings", "enabled", 1)
		phones = [{"phone": "+91 9999999991", "is_primary_phone": 0, "is_primary_mobile_no": 1}]
		create_contact(name="Test Contact", salutation="Mr", phones=phones)
		vmraid.db.commit()

	def test_for_successful_call(self):
		from .exotel_test_data import call_end_data, call_initiation_data

		api_method = "handle_incoming_call"
		end_call_api_method = "handle_end_call"

		self.emulate_api_call_from_exotel(api_method, call_initiation_data)
		self.emulate_api_call_from_exotel(end_call_api_method, call_end_data)
		call_log = vmraid.get_doc("Call Log", call_initiation_data.CallSid)

		self.assertEqual(call_log.get("from"), call_initiation_data.CallFrom)
		self.assertEqual(call_log.get("to"), call_initiation_data.DialWhomNumber)
		self.assertEqual(call_log.get("call_received_by"), self.test_employee_name)
		self.assertEqual(call_log.get("status"), "Completed")

	def test_for_disconnected_call(self):
		from .exotel_test_data import call_disconnected_data

		api_method = "handle_missed_call"
		self.emulate_api_call_from_exotel(api_method, call_disconnected_data)
		call_log = vmraid.get_doc("Call Log", call_disconnected_data.CallSid)
		self.assertEqual(call_log.get("from"), call_disconnected_data.CallFrom)
		self.assertEqual(call_log.get("to"), call_disconnected_data.DialWhomNumber)
		self.assertEqual(call_log.get("call_received_by"), self.test_employee_name)
		self.assertEqual(call_log.get("status"), "Canceled")

	def test_for_call_not_answered(self):
		from .exotel_test_data import call_not_answered_data

		api_method = "handle_missed_call"
		self.emulate_api_call_from_exotel(api_method, call_not_answered_data)
		call_log = vmraid.get_doc("Call Log", call_not_answered_data.CallSid)
		self.assertEqual(call_log.get("from"), call_not_answered_data.CallFrom)
		self.assertEqual(call_log.get("to"), call_not_answered_data.DialWhomNumber)
		self.assertEqual(call_log.get("call_received_by"), self.test_employee_name)
		self.assertEqual(call_log.get("status"), "No Answer")

	def emulate_api_call_from_exotel(self, api_method, data):
		self.post(
			f"/api/method/erpadda.erpadda_integrations.exotel_integration.{api_method}",
			data=vmraid.as_json(data),
			content_type="application/json",
			as_tuple=True,
		)
		# restart db connection to get latest data
		vmraid.connect()

	@classmethod
	def tearDownClass(cls):
		vmraid.db = cls.CURRENT_DB_CONNECTION
