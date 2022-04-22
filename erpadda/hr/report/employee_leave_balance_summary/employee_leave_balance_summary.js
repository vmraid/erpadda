// Copyright (c) 2016, VMRaid and contributors
// For license information, please see license.txt
/* eslint-disable */

vmraid.query_reports['Employee Leave Balance Summary'] = {
	filters: [
		{
			fieldname:'date',
			label: __('Date'),
			fieldtype: 'Date',
			reqd: 1,
			default: vmraid.datetime.now_date()
		},
		{
			fieldname:'company',
			label: __('Company'),
			fieldtype: 'Link',
			options: 'Company',
			reqd: 1,
			default: vmraid.defaults.get_user_default('Company')
		},
		{
			fieldname:'employee',
			label: __('Employee'),
			fieldtype: 'Link',
			options: 'Employee',
		},
		{
			fieldname:'department',
			label: __('Department'),
			fieldtype: 'Link',
			options: 'Department',
		}
	]
};
