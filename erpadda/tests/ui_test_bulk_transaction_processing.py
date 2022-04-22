import vmraid

from erpadda.bulk_transaction.doctype.bulk_transaction_logger.test_bulk_transaction_logger import (
	create_company,
	create_customer,
	create_item,
	create_so,
)


@vmraid.whitelist()
def create_records():
	create_company()
	create_customer()
	create_item()

	gd = vmraid.get_doc("Global Defaults")
	gd.set("default_company", "Test Bulk")
	gd.save()
	vmraid.clear_cache()
	create_so()
