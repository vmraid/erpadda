// Copyright (c) 2016, VMRaid and contributors
// For license information, please see license.txt
/* eslint-disable */

vmraid.query_reports["Item Variant Details"] = {
	"filters": [
		{
			reqd: 1,
			default: "",
			options: "Item",
			label: __("Item"),
			fieldname: "item",
			fieldtype: "Link",
			get_query: () => {
				return {
					filters: { "has_variants": 1 }
				}
			}
		}
	]
}
