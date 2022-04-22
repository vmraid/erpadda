// Copyright (c) 2015, VMRaid and Contributors
// License: GNU General Public License v3. See license.txt

vmraid.views.calendar["Training Event"] = {
	field_map: {
		"start": "start_time",
		"end": "end_time",
		"id": "name",
		"title": "event_name",
		"allDay": "allDay"
	},
	gantt: true,
	get_events_method: "vmraid.desk.calendar.get_events",
}
