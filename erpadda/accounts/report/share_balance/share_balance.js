// -*- coding: utf-8 -*-
// Copyright (c) 2017, VMRaid and contributors
// For license information, please see license.txt
/* eslint-disable */

vmraid.query_reports["Share Balance"] = {
	"filters": [
		{
			"fieldname":"date",
			"label": __("Date"),
			"fieldtype": "Date",
			"default": vmraid.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname":"shareholder",
			"label": __("Shareholder"),
			"fieldtype": "Link",
			"options": "Shareholder"
		}
	]
}
