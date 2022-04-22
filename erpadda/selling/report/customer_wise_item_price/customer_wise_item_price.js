// Copyright (c) 2016, VMRaid and contributors
// For license information, please see license.txt
/* eslint-disable */

vmraid.query_reports["Customer-wise Item Price"] = {
	"filters": [
		{
			"label": __("Customer"),
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer",
			"reqd": 1
		},
		{
			"label": __("Item"),
			"fieldname": "item",
			"fieldtype": "Link",
			"options": "Item",
			"get_query": () => {
				return {
					query: "erpadda.controllers.queries.item_query",
					filters: { 'is_sales_item': 1 }
				}
			}
		}
	]
}
