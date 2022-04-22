// Copyright (c) 2016, VMRaid and contributors
// For license information, please see license.txt
/* eslint-disable */


vmraid.query_reports["Territory-wise Sales"] = {
	"breadcrumb":"Selling",
	"filters": [
		{
			fieldname:"transaction_date",
			label: __("Transaction Date"),
			fieldtype: "DateRange",
			default: [vmraid.datetime.add_months(vmraid.datetime.get_today(),-1), vmraid.datetime.get_today()],
		},
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
		}
	]
};
