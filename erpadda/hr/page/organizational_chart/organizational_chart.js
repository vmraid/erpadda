vmraid.pages['organizational-chart'].on_page_load = function(wrapper) {
	vmraid.ui.make_app_page({
		parent: wrapper,
		title: __('Organizational Chart'),
		single_column: true
	});

	$(wrapper).bind('show', () => {
		vmraid.require('hierarchy-chart.bundle.js', () => {
			let organizational_chart = undefined;
			let method = 'erpadda.hr.page.organizational_chart.organizational_chart.get_children';

			if (vmraid.is_mobile()) {
				organizational_chart = new erpadda.HierarchyChartMobile('Employee', wrapper, method);
			} else {
				organizational_chart = new erpadda.HierarchyChart('Employee', wrapper, method);
			}

			vmraid.breadcrumbs.add('HR');
			organizational_chart.show();
		});
	});
};
