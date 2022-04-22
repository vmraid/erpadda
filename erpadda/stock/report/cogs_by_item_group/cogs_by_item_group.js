// Copyright (c) 2016, VMRaid and contributors
// For license information, please see license.txt
/* eslint-disable */


vmraid.query_reports["COGS By Item Group"] = {
	filters: [
    {
      label: __("Company"),
      fieldname: "company",
      fieldtype: "Link",
      options: "Company",
      mandatory: true,
      default: vmraid.defaults.get_user_default("Company"),
    },
    {
      label: __("From Date"),
      fieldname: "from_date",
      fieldtype: "Date",
      mandatory: true,
      default: vmraid.datetime.year_start(),
    },
    {
      label: __("To Date"),
      fieldname: "to_date",
      fieldtype: "Date",
      mandatory: true,
      default: vmraid.datetime.get_today(),
    },
	]
};
