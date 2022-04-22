import vmraid


def execute():
	name = vmraid.db.sql(
		""" select name from `tabPatch Log` \
		where \
			patch like 'execute:vmraid.db.sql("update `tabProduction Order` pro set description%' """
	)
	if not name:
		vmraid.db.sql(
			"update `tabProduction Order` pro \
			set \
				description = (select description from tabItem where name=pro.production_item) \
			where \
				ifnull(description, '') = ''"
		)
