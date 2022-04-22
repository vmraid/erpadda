# Copyright (c) 2017, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid


def execute():
	vmraid.reload_doc("setup", "doctype", "global_defaults", force=True)
	vmraid.reload_doc("stock", "doctype", "delivery_trip")
	vmraid.reload_doc("stock", "doctype", "delivery_stop", force=True)

	for trip in vmraid.get_all("Delivery Trip"):
		trip_doc = vmraid.get_doc("Delivery Trip", trip.name)

		status = {0: "Draft", 1: "Scheduled", 2: "Cancelled"}[trip_doc.docstatus]

		if trip_doc.docstatus == 1:
			visited_stops = [stop.visited for stop in trip_doc.delivery_stops]
			if all(visited_stops):
				status = "Completed"
			elif any(visited_stops):
				status = "In Transit"

		vmraid.db.set_value("Delivery Trip", trip.name, "status", status, update_modified=False)
