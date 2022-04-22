// Copyright (c) 2016, VMRaid and contributors
// For license information, please see license.txt
/* eslint-disable */

vmraid.query_reports["Incorrect Balance Qty After Transaction"] = {
	"filters": [
		{
			label: __("Company"),
			fieldtype: "Link",
			fieldname: "company",
			options: "Company",
			default: vmraid.defaults.get_user_default("Company"),
			reqd: 1
		},
		{
			label: __('Item Code'),
			fieldtype: 'Link',
			fieldname: 'item_code',
			options: 'Item'
		},
		{
			label: __('Warehouse'),
			fieldtype: 'Link',
			fieldname: 'warehouse'
		}
	]
};
