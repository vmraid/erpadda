vmraid.provide('vmraid.dashboards.chart_sources');

vmraid.dashboards.chart_sources["Warehouse wise Stock Value"] = {
	method: "erpadda.stock.dashboard_chart_source.warehouse_wise_stock_value.warehouse_wise_stock_value.get",
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: vmraid.defaults.get_user_default("Company")
		}
	]
};
