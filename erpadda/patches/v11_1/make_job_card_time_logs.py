# Copyright (c) 2015, VMRaid and Contributors
# License: GNU General Public License v3. See license.txt


import vmraid


def execute():
	vmraid.reload_doc("manufacturing", "doctype", "job_card_time_log")

	if vmraid.db.table_exists("Job Card") and vmraid.get_meta("Job Card").has_field(
		"actual_start_date"
	):
		time_logs = []
		for d in vmraid.get_all(
			"Job Card",
			fields=["actual_start_date", "actual_end_date", "time_in_mins", "name", "for_quantity"],
			filters={"docstatus": ("<", 2)},
		):
			if d.actual_start_date:
				time_logs.append(
					[
						d.actual_start_date,
						d.actual_end_date,
						d.time_in_mins,
						d.for_quantity,
						d.name,
						"Job Card",
						"time_logs",
						vmraid.generate_hash("", 10),
					]
				)

		if time_logs:
			vmraid.db.sql(
				""" INSERT INTO
                `tabJob Card Time Log`
                    (from_time, to_time, time_in_mins, completed_qty, parent, parenttype, parentfield, name)
                values {values}
            """.format(
					values=",".join(["%s"] * len(time_logs))
				),
				tuple(time_logs),
			)

		vmraid.reload_doc("manufacturing", "doctype", "job_card")
		vmraid.db.sql(
			""" update `tabJob Card` set total_completed_qty = for_quantity,
            total_time_in_mins = time_in_mins where docstatus < 2 """
		)
