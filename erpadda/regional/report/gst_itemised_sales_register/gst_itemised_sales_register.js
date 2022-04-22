// Copyright (c) 2016, VMRaid and contributors
// For license information, please see license.txt
/* eslint-disable */

{% include "erpadda/accounts/report/item_wise_sales_register/item_wise_sales_register.js" %}
{% include "erpadda/regional/report/india_gst_common/india_gst_common.js" %}

let filters = vmraid.query_reports["Item-wise Sales Register"]["filters"];

// Add GSTIN filter
filters = filters.concat({
    "fieldname":"company_gstin",
    "label": __("Company GSTIN"),
    "fieldtype": "Select",
    "placeholder":"Company GSTIN",
    "options": [""],
    "width": "80"
}, {
    "fieldname":"invoice_type",
    "label": __("Invoice Type"),
    "fieldtype": "Select",
    "placeholder":"Invoice Type",
    "options": ["", "Regular", "SEZ", "Export", "Deemed Export"]
});

// Handle company on change
for (var i = 0; i < filters.length; ++i) {
    if (filters[i].fieldname === 'company') {
        filters[i].on_change = fetch_gstins;
    }
}

vmraid.query_reports["GST Itemised Sales Register"] = { "filters": filters, "onload": fetch_gstins };
