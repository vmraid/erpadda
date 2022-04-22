// Copyright (c) 2016, VMRaid and contributors
// For license information, please see license.txt
/* eslint-disable */

vmraid.query_reports["Sales Analytics"] = {
	"filters": [
		{
			fieldname: "tree_type",
			label: __("Tree Type"),
			fieldtype: "Select",
			options: ["Customer Group", "Customer", "Item Group", "Item", "Territory", "Order Type", "Project"],
			default: "Customer",
			reqd: 1
		},
		{
			fieldname: "doc_type",
			label: __("based_on"),
			fieldtype: "Select",
			options: ["Sales Order","Delivery Note","Sales Invoice"],
			default: "Sales Invoice",
			reqd: 1
		},
		{
			fieldname: "value_quantity",
			label: __("Value Or Qty"),
			fieldtype: "Select",
			options: [
				{ "value": "Value", "label": __("Value") },
				{ "value": "Quantity", "label": __("Quantity") },
			],
			default: "Value",
			reqd: 1
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: vmraid.defaults.get_user_default("year_start_date"),
			reqd: 1
		},
		{
			fieldname:"to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: vmraid.defaults.get_user_default("year_end_date"),
			reqd: 1
		},
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: vmraid.defaults.get_user_default("Company"),
			reqd: 1
		},
		{
			fieldname: "range",
			label: __("Range"),
			fieldtype: "Select",
			options: [
				{ "value": "Weekly", "label": __("Weekly") },
				{ "value": "Monthly", "label": __("Monthly") },
				{ "value": "Quarterly", "label": __("Quarterly") },
				{ "value": "Yearly", "label": __("Yearly") }
			],
			default: "Monthly",
			reqd: 1
		}
	],
	after_datatable_render: function(datatable_obj) {
		$(datatable_obj.wrapper).find(".dt-row-0").find('input[type=checkbox]').click();
	},
	get_datatable_options(options) {
		return Object.assign(options, {
			checkboxColumn: true,
			events: {
				onCheckRow: function (data) {
					if (!data) return;
					const data_doctype = $(
						data[2].html
					)[0].attributes.getNamedItem("data-doctype").value;
					const tree_type = vmraid.query_report.filters[0].value;
					if (data_doctype != tree_type) return;

					const row_name = data[2].content;
					const raw_data = vmraid.query_report.chart.data;
					const new_datasets = raw_data.datasets;
					const element_found = new_datasets.some(
						(element, index, array) => {
							if (element.name == row_name) {
								array.splice(index, 1);
								return true;
							}
							return false;
						}
					);
					const slice_at = { Customer: 4, Item: 5 }[tree_type] || 3;

					if (!element_found) {
						new_datasets.push({
							name: row_name,
							values: data
								.slice(slice_at, data.length - 1)
								.map(column => column.content),
						});
					}

					const new_data = {
						labels: raw_data.labels,
						datasets: new_datasets,
					};

					vmraid.query_report.render_chart({
						data: new_data,
						type: "line",
					});

					vmraid.query_report.raw_chart_data = new_data;
				},
			},
		});
	},
};