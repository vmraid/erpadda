// Copyright (c) 2016, VMRaid and contributors
// For license information, please see license.txt
/* eslint-disable */

vmraid.query_reports['Billed Items To Be Received'] = {
	'filters': [
		{
			'label': __('Company'),
			'fieldname': 'company',
			'fieldtype': 'Link',
			'options': 'Company',
			'reqd': 1,
			'default': vmraid.defaults.get_default('Company')
		},
		{
			'label': __('As on Date'),
			'fieldname': 'posting_date',
			'fieldtype': 'Date',
			'reqd': 1,
			'default': get_today()
		},
		{
			'label': __('Purchase Invoice'),
			'fieldname': 'purchase_invoice',
			'fieldtype': 'Link',
			'options': 'Purchase Invoice'
		}
	]
};
