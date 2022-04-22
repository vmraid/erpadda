import vmraid


def execute():
	vmraid.reload_doc("setup", "doctype", "currency_exchange")
	vmraid.db.sql("""update `tabCurrency Exchange` set for_buying = 1, for_selling = 1""")
