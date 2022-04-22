vmraid.provide('vmraid.dashboards.chart_sources');

vmraid.dashboards.chart_sources["Account Balance Timeline"] = {
	method: "erpadda.accounts.dashboard_chart_source.account_balance_timeline.account_balance_timeline.get",
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: vmraid.defaults.get_user_default("Company"),
			reqd: 1
		},
		{
			fieldname: "account",
			label: __("Account"),
			fieldtype: "Link",
			options: "Account",
			reqd: 1
		},
	]
};
