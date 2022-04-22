// Copyright (c) 2015, VMRaid and Contributors
// License: GNU General Public License v3. See license.txt


vmraid.query_reports["Absent Student Report"] = {
	"filters": [
		{
			"fieldname":"date",
			"label": __("Date"),
			"fieldtype": "Date",
			"default": vmraid.datetime.get_today(),
			"reqd": 1
		}
	]
}
