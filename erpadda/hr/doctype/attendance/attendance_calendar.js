// Copyright (c) 2018, VMRaid and contributors
// For license information, please see license.txt
vmraid.views.calendar["Attendance"] = {
	options: {
		header: {
			left: 'prev,next today',
			center: 'title',
			right: 'month'
		}
	},
	get_events_method: "erpadda.hr.doctype.attendance.attendance.get_events"
};
