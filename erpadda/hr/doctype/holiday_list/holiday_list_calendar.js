// Copyright (c) 2015, VMRaid and Contributors
// License: GNU General Public License v3. See license.txt

vmraid.views.calendar["Holiday List"] = {
	field_map: {
		"start": "holiday_date",
		"end": "holiday_date",
		"id": "name",
		"title": "description",
		"allDay": "allDay"
	},
	order_by: `from_date`,
	get_events_method: "erpadda.hr.doctype.holiday_list.holiday_list.get_events",
	filters: [
		{
			'fieldtype': 'Link',
			'fieldname': 'holiday_list',
			'options': 'Holiday List',
			'label': __('Holiday List')
		}
	]
}
