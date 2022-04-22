vmraid.provide('vmraid.dashboards.chart_sources');

vmraid.dashboards.chart_sources["Top 10 Pledged Loan Securities"] = {
	method: "erpadda.loan_management.dashboard_chart_source.top_10_pledged_loan_securities.top_10_pledged_loan_securities.get_data",
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
